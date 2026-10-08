import { expect, test } from '@playwright/test';

async function finishOnboarding(page: import('@playwright/test').Page, label: string) {
  await page.goto('/');
  await page.getByRole('button', { name: 'Create a free account' }).click();
  await page
    .getByRole('textbox', { name: 'Email', exact: true })
    .fill(`goals-${label}-${Date.now()}@example.com`);
  await page.getByRole('button', { name: 'Continue', exact: true }).click();
  await page.getByRole('textbox', { name: 'Your name' }).fill('Goals Tester');
  await page.getByRole('checkbox', { name: 'sleep', exact: true }).focus();
  await page.keyboard.press('Space');
  await page.getByRole('button', { name: 'Continue to my dashboard' }).click();
  await expect(page.getByRole('heading', { name: 'Your goals' })).toBeVisible();
}

test('creates, reads, edits, archives, and soft-deletes a goal from the dashboard', async ({
  page,
}) => {
  await finishOnboarding(page, 'lifecycle');
  await expect(page.getByText('No goals yet')).toBeVisible();
  await page.getByRole('button', { name: '+ Create goal' }).click();
  await page.getByLabel('Goal title').fill('Improve my sleep routine');
  await page.getByLabel('Description (optional)').fill('Create a steady evening routine');
  await page.getByRole('button', { name: 'Create goal', exact: true }).click();
  const card = page.locator('.goal-card').filter({ hasText: 'Improve my sleep routine' });
  await expect(card).toBeVisible();
  await card.getByRole('button', { name: 'View' }).click();
  await expect(page.getByRole('region', { name: 'Goal details' })).toBeFocused();
  await expect(page.getByText('Create a steady evening routine')).toBeVisible();
  await page.getByRole('button', { name: 'Close details' }).click();
  await card.getByRole('button', { name: 'Edit' }).click();
  await page.getByLabel('Goal title').fill('Build a steady sleep routine');
  await page.getByLabel('Status').selectOption('paused');
  await page.getByRole('button', { name: 'Save goal' }).click();
  await expect(
    page.locator('.goal-card').filter({ hasText: 'Build a steady sleep routine' }),
  ).toContainText('paused');
  const updatedCard = page
    .locator('.goal-card')
    .filter({ hasText: 'Build a steady sleep routine' });
  await updatedCard.getByRole('button', { name: 'Archive' }).click();
  await expect(updatedCard).toContainText('archived');
  page.once('dialog', (dialog) => void dialog.accept());
  const deleteResponse = page.waitForResponse(
    (response) =>
      response.url().includes('/api/v1/me/goals/') && response.request().method() === 'DELETE',
  );
  await updatedCard.getByRole('button', { name: 'Delete' }).click();
  const deletedResponse = await deleteResponse;
  expect(deletedResponse.status()).toBe(204);
  await expect(page.getByText('No goals yet')).toBeVisible();
  await expect(
    page.getByRole('status').filter({ hasText: 'Goal removed from your list.' }),
  ).toBeVisible();
});

test('supports keyboard goal creation, focus return, and safe unsafe-content errors on mobile', async ({
  page,
}) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await finishOnboarding(page, 'keyboard');
  const create = page.getByRole('button', { name: '+ Create goal' });
  await create.focus();
  await page.keyboard.press('Enter');
  const title = page.getByLabel('Goal title');
  await expect(title).toBeFocused();
  await page.keyboard.type('Drink more water');
  await page.keyboard.press('Tab');
  await expect(page.getByLabel('Description (optional)')).toBeFocused();
  const createGoalButton = page.getByRole('button', { name: 'Create goal', exact: true });
  for (let step = 0; step < 12; step += 1) {
    await page.keyboard.press('Tab');
    if (await createGoalButton.evaluate((element) => element === document.activeElement)) break;
  }
  await expect(createGoalButton).toBeFocused();
  await page.keyboard.press('Enter');
  const card = page.locator('.goal-card').filter({ hasText: 'Drink more water' });
  await expect(card).toBeVisible();
  await card.getByRole('button', { name: 'Edit' }).focus();
  await page.keyboard.press('Enter');
  await expect(title).toBeFocused();
  await title.fill('Increase my medication dosage');
  await page.getByRole('button', { name: 'Save goal' }).click();
  const alert = page.locator('.goal-form-wrap').getByRole('alert');
  await expect(alert).toBeVisible();
  await expect(alert).not.toContainText('medication dosage');
  await expect(title).toBeFocused();
  await title.fill('Drink more water');
  await page.getByRole('button', { name: 'Cancel' }).click();
  await expect(create).toBeFocused();
  expect(
    await page.evaluate(
      () => document.documentElement.scrollWidth <= document.documentElement.clientWidth,
    ),
  ).toBe(true);
});

test('shows a calm retry state for goal API failures without rendering server details', async ({
  page,
}) => {
  await page.route('**/api/v1/me/goals', async (route) => {
    if (route.request().method() === 'GET') {
      await route.fulfill({
        status: 503,
        contentType: 'application/json',
        body: JSON.stringify({
          error: { code: 'internal_error', message: 'secret backend detail' },
        }),
      });
    } else {
      await route.continue();
    }
  });
  await finishOnboarding(page, 'api-error');
  const alert = page.locator('.goals-panel').getByRole('alert');
  await expect(alert).toContainText('Goals are temporarily unavailable.');
  await expect(alert).not.toContainText('secret backend detail');
});

test('shows a sign-in recovery state when the goal API reports an expired session', async ({
  page,
}) => {
  await page.route('**/api/v1/me/goals', async (route) => {
    if (route.request().method() === 'GET') {
      await route.fulfill({
        status: 401,
        contentType: 'application/json',
        body: JSON.stringify({
          error: { code: 'unauthenticated', message: 'private server detail' },
        }),
      });
    } else {
      await route.continue();
    }
  });
  await finishOnboarding(page, 'expired-session');
  const alert = page.locator('.goals-panel').getByRole('alert');
  await expect(alert).toContainText('Your session has ended.');
  await expect(alert).not.toContainText('private server detail');
  await expect(alert.getByRole('button', { name: 'Return to sign in' })).toBeVisible();
});

test('keeps the session visible and focuses a retry action when sign out fails', async ({
  page,
}) => {
  await finishOnboarding(page, 'logout-retry');
  let attempts = 0;
  await page.route('**/api/v1/auth/logout', async (route) => {
    attempts += 1;
    if (attempts === 1) {
      await route.fulfill({
        status: 503,
        contentType: 'application/json',
        body: JSON.stringify({
          error: { code: 'auth_dependency_unavailable', message: 'Private' },
        }),
      });
    } else {
      await route.fulfill({ status: 204, body: '' });
    }
  });
  await page.getByRole('button', { name: 'Sign out' }).click();
  const alert = page.locator('.logout-error');
  await expect(alert).toContainText('Sign out did not complete.');
  await expect(alert).toBeFocused();
  await expect(page.getByRole('heading', { name: 'Your goals' })).toBeVisible();
  await page.getByRole('button', { name: 'Retry sign out' }).click();
  await expect(page.getByRole('button', { name: 'Sign in' })).toBeVisible();
});

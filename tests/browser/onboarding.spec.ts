import { expect, test, type Locator, type Page } from '@playwright/test';

async function tabTo(page: Page, target: Locator) {
  for (let step = 0; step < 20; step += 1) {
    await page.keyboard.press('Tab');
    if (await target.evaluate((element) => element === document.activeElement)) return;
  }
  throw new Error('Control could not be reached using Tab');
}

async function registerWithKeyboard(page: Page) {
  await page.goto('/');
  await tabTo(page, page.getByRole('button', { name: 'Create a free account' }));
  await page.keyboard.press('Enter');
  await tabTo(page, page.getByRole('textbox', { name: 'Email', exact: true }));
  await page.keyboard.type(`keyboard-${Date.now()}@example.com`);
  await page.keyboard.press('Tab');
  await expect(page.getByRole('button', { name: 'Continue', exact: true })).toBeFocused();
  await page.keyboard.press('Enter');
  await expect(page.getByRole('group', { name: 'What would you like to focus on?' })).toBeVisible();
}

test('tabs through every focus option, toggles with Space, and completes onboarding without a mouse', async ({
  page,
}, testInfo) => {
  await registerWithKeyboard(page);
  const continueButton = page.getByRole('button', { name: 'Continue to my dashboard' });
  await expect(continueButton).toBeDisabled();
  await tabTo(page, page.getByRole('textbox', { name: 'Your name' }));
  await page.keyboard.type('Keyboard Tester');
  await page.keyboard.press('Tab');
  await expect(page.getByRole('combobox', { name: 'Timezone' })).toBeFocused();
  for (const area of [
    'sleep',
    'movement',
    'nutrition',
    'stress',
    'hydration',
    'mindfulness',
    'routine',
  ]) {
    await page.keyboard.press('Tab');
    const option = page.getByRole('checkbox', { name: area, exact: true });
    await expect(option).toBeFocused();
    const label = option.locator('..');
    await expect(label).toHaveCSS('outline-style', 'solid');
    await expect(label).toHaveCSS('outline-width', '3px');
    if (area === 'sleep')
      await page.screenshot({ path: testInfo.outputPath('keyboard-focus.png') });
    await page.keyboard.press('Space');
    await expect(option).toBeChecked();
    await expect(continueButton).toBeEnabled();
    await page.keyboard.press('Space');
    await expect(option).not.toBeChecked();
    await expect(continueButton).toBeDisabled();
  }
  await page.keyboard.press('Space');
  await page.keyboard.press('Tab');
  await expect(
    page.getByRole('checkbox', { name: /Allow future personalization memory/ }),
  ).toBeFocused();
  await page.keyboard.press('Tab');
  await expect(continueButton).toBeFocused();
  await page.keyboard.press('Enter');
  await expect(page.getByRole('heading', { name: 'Welcome back, Keyboard Tester' })).toBeVisible();
  await expect(page.getByText('✓ Complete', { exact: true })).toBeVisible();
});

test('announces an API form error and allows keyboard correction and completion', async ({
  page,
}) => {
  await registerWithKeyboard(page);
  await tabTo(page, page.getByRole('textbox', { name: 'Your name' }));
  await page.keyboard.type('   ');
  await page.keyboard.press('Tab');
  await page.keyboard.press('Tab');
  await expect(page.getByRole('checkbox', { name: 'sleep', exact: true })).toBeFocused();
  await page.keyboard.press('Space');
  await tabTo(page, page.getByRole('button', { name: 'Continue to my dashboard' }));
  await page.keyboard.press('Enter');
  const alert = page.locator('#app-form-error');
  await expect(alert).toBeVisible();
  await expect(alert).toHaveAttribute('role', 'alert');
  await expect(alert).toBeFocused();
  await expect(page.locator('form')).toHaveAttribute('aria-describedby', 'app-form-error');
  await tabTo(page, page.getByRole('textbox', { name: 'Your name' }));
  await page.keyboard.press('ControlOrMeta+A');
  await page.keyboard.type('Corrected Tester');
  await tabTo(page, page.getByRole('button', { name: 'Continue to my dashboard' }));
  await page.keyboard.press('Enter');
  await expect(page.getByRole('heading', { name: 'Welcome back, Corrected Tester' })).toBeVisible();
});

test('restores the latest memory consent decision after a page reload', async ({ page }) => {
  await page.goto('/');
  await page.getByRole('button', { name: 'Create a free account' }).click();
  await page
    .getByRole('textbox', { name: 'Email', exact: true })
    .fill(`consent-restore-${Date.now()}@example.com`);
  await page.getByRole('button', { name: 'Continue', exact: true }).click();
  await page.getByRole('textbox', { name: 'Your name' }).fill('Consent Tester');
  await page.getByRole('checkbox', { name: 'sleep', exact: true }).focus();
  await page.keyboard.press('Space');
  const memoryChoice = page.getByRole('checkbox', {
    name: /Allow future personalization memory/,
  });
  await memoryChoice.focus();
  await page.keyboard.press('Space');
  await page.getByRole('button', { name: 'Continue to my dashboard' }).click();
  await expect(page.getByRole('heading', { name: 'Welcome back, Consent Tester' })).toBeVisible();

  await page.reload();
  await expect(page.getByRole('heading', { name: 'Welcome back, Consent Tester' })).toBeVisible();
  await page.getByRole('button', { name: 'Edit wellness setup' }).click();
  await expect(memoryChoice).toBeChecked();
});

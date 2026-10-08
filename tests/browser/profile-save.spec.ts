import { expect, test } from '@playwright/test';

test('profile and wellness edits send only writable fields and persist after reload', async ({
  page,
}) => {
  await page.goto('/');
  await page.getByRole('button', { name: 'Create a free account' }).click();
  await page
    .getByRole('textbox', { name: 'Email', exact: true })
    .fill(`profile-${Date.now()}@example.com`);
  await page.getByRole('button', { name: 'Continue', exact: true }).click();
  await page.getByRole('textbox', { name: 'Your name' }).fill('Original Tester');
  await page.getByRole('checkbox', { name: 'sleep', exact: true }).focus();
  await page.keyboard.press('Space');
  await page.getByRole('button', { name: 'Continue to my dashboard' }).click();
  await expect(page.getByRole('heading', { name: 'Welcome back, Original Tester' })).toBeVisible();
  await page.getByRole('button', { name: 'Profile', exact: true }).click();
  await page.getByRole('textbox', { name: 'Name', exact: true }).fill('Updated Tester');
  await page.getByRole('textbox', { name: 'Locale' }).fill('en-GB');
  await page.getByRole('textbox', { name: 'Timezone' }).fill('Europe/London');
  await page.getByRole('checkbox', { name: 'movement', exact: true }).focus();
  await page.keyboard.press('Space');
  const responses = Promise.all(
    ['/me/profile', '/me/wellness-profile'].map((path) =>
      page.waitForResponse(
        (response) => response.url().endsWith(path) && response.request().method() === 'PATCH',
      ),
    ),
  );
  await page.getByRole('button', { name: 'Save changes', exact: true }).click();
  const [profile, wellness] = await responses;
  expect(profile!.request().postDataJSON()).toEqual({
    display_name: 'Updated Tester',
    locale: 'en-GB',
    timezone: 'Europe/London',
  });
  expect(wellness!.request().postDataJSON()).toEqual({ wellness_areas: ['sleep', 'movement'] });
  for (const response of [profile!, wellness!]) {
    expect(response.status()).toBe(200);
    expect(response.headers()['cache-control']).toBe('private, no-store');
    const body = await response.json();
    expect(body.meta.request_id).toBe(response.headers()['x-request-id']);
    expect(body.warnings).toEqual([]);
    expect(body.data.account_id).toEqual(expect.any(String));
    expect(body.data.updated_at).toEqual(expect.any(String));
  }
  await expect(page.getByRole('button', { name: 'Saved ✓' })).toBeVisible();
  await page.reload();
  await expect(page.getByRole('heading', { name: 'Welcome back, Updated Tester' })).toBeVisible();
  await page.getByRole('button', { name: 'Profile', exact: true }).click();
  await expect(page.getByRole('textbox', { name: 'Locale' })).toHaveValue('en-GB');
  await expect(page.getByRole('textbox', { name: 'Timezone' })).toHaveValue('Europe/London');
  await expect(page.getByRole('checkbox', { name: 'movement', exact: true })).toBeChecked();
});

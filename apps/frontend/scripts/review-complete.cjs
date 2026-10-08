const fs = require('node:fs');
const path = require('node:path');
const { chromium, expect } = require('@playwright/test');
const AxeBuilder = require('@axe-core/playwright').default;
const root = path.resolve(__dirname, '../../..');
const secrets = JSON.parse(fs.readFileSync(path.join(root, '.integration/runtime/secrets.json'), 'utf8'));
const fixtures = JSON.parse(fs.readFileSync(path.join(root, '.integration/runtime/demo-fixtures.json'), 'utf8'));
const output = path.join(root, 'artifacts/browser');
const base = process.env.SMARTEDU_FRONTEND_URL || 'http://localhost:5173';
fs.mkdirSync(output, { recursive: true });
const routes = {
  student: ['', '/attendance', '/timetable', '/learning', '/assessments', `/assessments/${fixtures['assessment-assignment'].id}`, '/facilities'],
  teacher: ['', '/attendance', '/timetable', '/learning', '/assessments', '/announcements', '/facilities'],
  admin: ['', '/users', '/academic', '/scheduling', '/facilities', '/notifications', '/reporting', '/platform']
};
(async () => {
  const browser = await chromium.launch({ channel: 'chrome', headless: true });
  const results = [];
  for (const role of ['student', 'teacher', 'admin']) {
    const context = await browser.newContext({ viewport: { width: 1440, height: 1000 }, reducedMotion: 'reduce' });
    const page = await context.newPage();
    let errors = [];
    page.on('pageerror', error => errors.push(error.message));
    page.on('response', response => { if (response.status() >= 400 && !response.url().includes('/auth/refresh')) errors.push(`${response.status()} ${new URL(response.url()).pathname}`); });
    await page.goto(`${base}/login`);
    await page.getByLabel('Email').fill(`${role}@demo.example.edu`);
    await page.getByLabel('Password').fill(secrets[role === 'admin' ? 'DEMO_PASSWORD' : `${role.toUpperCase()}_PASSWORD`]);
    await page.getByRole('button', { name: /sign in/i }).click();
    await page.waitForURL(`**/app/${role}`, { timeout: 20000 });
    for (const route of [...routes[role].map(suffix => `/app/${role}${suffix}`), '/app/notifications', '/app/profile']) {
      errors = [];
      const start = performance.now();
      await page.goto(`${base}${route}`);
      await page.locator('main h1').waitFor({ timeout: 15000 });
      await expect(page.getByRole('status').filter({ hasText: /Loading/i })).toHaveCount(0, { timeout: 15000 });
      const milliseconds = Math.round(performance.now() - start);
      const alerts = await page.getByRole('alert').allTextContents();
      const axe = await new AxeBuilder({ page }).withTags(['wcag2a', 'wcag2aa', 'wcag21aa']).analyze();
      const violations = axe.violations.map(v => ({ id: v.id, impact: v.impact, nodes: v.nodes.map(n => n.target) }));
      const widths = [];
      for (const width of [320, 375, 768, 1024, 1440]) {
        await page.setViewportSize({ width, height: 900 });
        await page.evaluate(() => new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve))));
        widths.push({ width, overflow: await page.evaluate(() => document.documentElement.scrollWidth > innerWidth) });
      }
      results.push({ role, route, milliseconds, errors: [...new Set(errors)], alerts, violations, widths });
      fs.writeFileSync(path.join(output, 'review.json'), JSON.stringify(results, null, 2));
      console.log(JSON.stringify({ role, route, milliseconds, errors: [...new Set(errors)], violations: violations.map(v => v.id), overflow: widths.filter(w => w.overflow).map(w => w.width) }));
      if (route === `/app/${role}`) {
        await page.screenshot({ path: path.join(output, `${role}-desktop.png`), fullPage: true });
        await page.getByRole('button', { name: /Switch to dark theme/i }).click();
        await page.screenshot({ path: path.join(output, `${role}-dark.png`), fullPage: true });
        const darkAxe = await new AxeBuilder({ page }).withTags(['wcag2a','wcag2aa','wcag21aa']).analyze();
        results.push({ role, theme: 'dark', violations: darkAxe.violations.map(v => ({ id: v.id, nodes: v.nodes.map(n => n.target) })) });
        await page.setViewportSize({ width: 320, height: 900 });
        await page.screenshot({ path: path.join(output, `${role}-mobile.png`), fullPage: true });
        await page.getByRole('button', { name: 'Open navigation' }).click();
        await expect(page.getByRole('dialog', { name: 'Navigation', exact: true })).toBeVisible();
        await page.keyboard.press('Escape');
        await expect(page.getByRole('dialog', { name: 'Navigation', exact: true })).not.toBeVisible();
        await page.setViewportSize({ width: 1440, height: 900 });
        await page.keyboard.press('Control+k');
        await expect(page.getByRole('dialog', { name: 'Find your next page' })).toBeVisible();
        await expect(page.getByRole('textbox', { name: 'Search workspace pages' })).toBeFocused();
        await page.keyboard.press('Escape');
        await page.getByRole('button', { name: /Switch to light theme/i }).click();
      }
    }
    await context.close();
  }
  fs.writeFileSync(path.join(output, 'review.json'), JSON.stringify(results, null, 2));
  await browser.close();
  if (results.some(r => r.errors?.length || r.alerts?.length || r.violations?.length || r.widths?.some(w => w.overflow))) process.exitCode = 1;
})().catch(error => { console.error(error.message); process.exitCode = 1; });

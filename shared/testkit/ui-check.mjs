#!/usr/bin/env node
// UI検証スクリプト（Playwright / Chromium）
// usage: node ui-check.mjs <URLまたはHTMLファイルパス> [--scenario steps.json] [--out verify]
//
// PC(1280x800) + スマホ(375x812) の2ビューポートでページを開き、フルページスクリーンショットと
// console error / pageerror / 失敗したnetwork requestを収集する。
// --scenario を渡すとPCビューポートでクリック/入力/待機/スクリーンショットのシナリオを実行できる。
//
// 出力: <out>/screenshots/*.png, <out>/ui-report.json
// 終了コード: エラー0件かつ全シナリオステップ成功 = 0, それ以外 = 1, playwright未インストール = 2

import path from "node:path";
import fs from "node:fs";
import { pathToFileURL } from "node:url";

function parseArgs(argv) {
  const args = { target: null, scenario: null, out: "verify" };
  const rest = [...argv];
  args.target = rest.shift() ?? null;
  while (rest.length > 0) {
    const flag = rest.shift();
    if (flag === "--scenario") {
      args.scenario = rest.shift() ?? null;
    } else if (flag === "--out") {
      args.out = rest.shift() ?? "verify";
    }
  }
  return args;
}

function resolveTargetUrl(target) {
  if (/^https?:\/\//i.test(target)) {
    return target;
  }
  // Windowsパス対応: バックスラッシュ→スラッシュ変換 + 絶対パス化
  const normalized = target.replace(/\\/g, "/");
  const absolute = path.isAbsolute(normalized)
    ? normalized
    : path.resolve(process.cwd(), normalized);
  return pathToFileURL(absolute).href;
}

async function loadScenario(scenarioPath) {
  if (!scenarioPath) return [];
  const raw = fs.readFileSync(path.resolve(process.cwd(), scenarioPath), "utf-8");
  const steps = JSON.parse(raw);
  if (!Array.isArray(steps)) {
    throw new Error("シナリオファイルはJSON配列である必要があります");
  }
  return steps;
}

function isHarmlessNetworkError(url) {
  return /favicon\.ico$/i.test(url);
}

function attachErrorCollectors(page, viewportName, errors) {
  page.on("console", (msg) => {
    if (msg.type() === "error") {
      errors.push({ type: "console", message: msg.text(), viewport: viewportName });
    }
  });
  page.on("pageerror", (err) => {
    errors.push({ type: "pageerror", message: String(err?.message ?? err), viewport: viewportName });
  });
  page.on("requestfailed", (request) => {
    const url = request.url();
    const failure = request.failure();
    const message = `${url} — ${failure?.errorText ?? "unknown error"}${isHarmlessNetworkError(url) ? " (harmless: favicon)" : ""}`;
    errors.push({ type: "network", message, viewport: viewportName });
  });
  page.on("response", (response) => {
    const status = response.status();
    if (status >= 400) {
      const url = response.url();
      const message = `${url} — HTTP ${status}${isHarmlessNetworkError(url) ? " (harmless: favicon)" : ""}`;
      errors.push({ type: "network", message, viewport: viewportName });
    }
  });
}

async function runScenario(page, steps, screenshotsDir) {
  const results = [];
  for (let i = 0; i < steps.length; i++) {
    const step = steps[i];
    const stepNo = i + 1;
    try {
      if (step.action === "click") {
        await page.click(step.selector);
      } else if (step.action === "fill") {
        await page.fill(step.selector, step.value ?? "");
      } else if (step.action === "waitFor") {
        await page.waitForSelector(step.selector, { timeout: 10000 });
      } else if (step.action === "screenshot") {
        const name = step.name ?? `step-${stepNo}`;
        const file = path.join(screenshotsDir, `${stepNo}-${name}.png`);
        await page.screenshot({ path: file, fullPage: true });
      } else {
        throw new Error(`未知のaction: ${step.action}`);
      }
      results.push({ step: stepNo, action: step.action, ok: true, error: null });
    } catch (err) {
      results.push({ step: stepNo, action: step.action, ok: false, error: String(err?.message ?? err) });
    }
  }
  return results;
}

async function main() {
  const args = parseArgs(process.argv.slice(2));
  if (!args.target) {
    console.error("usage: node ui-check.mjs <URLまたはHTMLファイルパス> [--scenario steps.json] [--out verify]");
    process.exit(2);
  }

  let chromium;
  try {
    ({ chromium } = await import("playwright"));
  } catch {
    console.error(
      "❌ playwright が見つかりません。次を実行してください: npm i -D playwright && npx playwright install chromium"
    );
    process.exit(2);
    return;
  }

  const url = resolveTargetUrl(args.target);
  const outDir = path.resolve(process.cwd(), args.out);
  const screenshotsDir = path.join(outDir, "screenshots");
  fs.mkdirSync(screenshotsDir, { recursive: true });

  const errors = [];
  const viewports = [];
  let scenarioResults = [];

  const browser = await chromium.launch();
  try {
    const pcContext = await browser.newContext({ viewport: { width: 1280, height: 800 } });
    const pcPage = await pcContext.newPage();
    attachErrorCollectors(pcPage, "pc", errors);
    await pcPage.goto(url, { waitUntil: "load" });
    const pcScreenshot = path.join(screenshotsDir, "pc-1280x800.png");
    await pcPage.screenshot({ path: pcScreenshot, fullPage: true });
    viewports.push({ name: "pc", screenshot: pcScreenshot });

    let steps = [];
    try {
      steps = await loadScenario(args.scenario);
    } catch (err) {
      errors.push({ type: "console", message: `シナリオ読み込み失敗: ${String(err?.message ?? err)}`, viewport: "pc" });
    }
    if (steps.length > 0) {
      scenarioResults = await runScenario(pcPage, steps, screenshotsDir);
    }

    await pcContext.close();

    const mobileContext = await browser.newContext({ viewport: { width: 375, height: 812 } });
    const mobilePage = await mobileContext.newPage();
    attachErrorCollectors(mobilePage, "mobile", errors);
    await mobilePage.goto(url, { waitUntil: "load" });
    const mobileScreenshot = path.join(screenshotsDir, "mobile-375x812.png");
    await mobilePage.screenshot({ path: mobileScreenshot, fullPage: true });
    viewports.push({ name: "mobile", screenshot: mobileScreenshot });
    await mobileContext.close();
  } finally {
    await browser.close();
  }

  const scenarioOk = scenarioResults.every((r) => r.ok);
  const pass = errors.length === 0 && scenarioOk;

  const report = {
    url,
    timestamp: new Date().toISOString(),
    viewports,
    errors,
    scenario: scenarioResults,
    pass,
  };

  const reportPath = path.join(outDir, "ui-report.json");
  fs.writeFileSync(reportPath, JSON.stringify(report, null, 2), "utf-8");

  if (pass) {
    console.log(
      `✅ PASS — エラー0件、スクリーンショット${viewports.length}枚保存: ${path.relative(process.cwd(), screenshotsDir)}`
    );
    process.exit(0);
  } else {
    console.log(
      `❌ FAIL — console/pageerror/networkエラー${errors.length}件、シナリオ失敗${scenarioResults.filter((r) => !r.ok).length}件（詳細: ${path.relative(process.cwd(), reportPath)}）`
    );
    process.exit(1);
  }
}

main().catch((err) => {
  console.error("予期しないエラー:", err);
  process.exit(1);
});

// Сборка карточки вызова в один ESM-бандл (Lit вшит). Артефакт коммитится в
// custom_components/.../www/ — HACS раздаёт его как Lovelace-ресурс, без сборки.
import { build, context } from "esbuild";
import process from "node:process";

const OUT = "../custom_components/my_dom_ru/www/mdr-intercom-call-card.js";

/** @type {import("esbuild").BuildOptions} */
const opts = {
  entryPoints: ["src/mdr-intercom-call-card.ts"],
  bundle: true,
  format: "esm",
  target: "es2021",
  minify: true,
  sourcemap: false,
  legalComments: "none",
  // Lit production-режим (убирает dev-mode warnings в консоли HA).
  define: { "process.env.NODE_ENV": '"production"' },
  outfile: OUT,
  banner: {
    js: "/* mdr-intercom-call-card — собранный бандл. Источник: frontend/src/. Не редактировать вручную. */",
  },
};

if (process.argv.includes("--watch")) {
  const ctx = await context(opts);
  await ctx.watch();
  console.log("watching frontend/src → " + OUT);
} else {
  await build(opts);
  console.log("built → " + OUT);
}

import * as crypto from "node:crypto";
import * as fs from "node:fs";
import * as path from "node:path";

const botDir = process.env.MAKEFUN_BOT_DIR ?? import.meta.dirname;
const outDir = process.env.MAKEFUN_OUTPUT_DIR ?? "/output";
const src = path.join(botDir, "meme.png");
const dst = path.join(outDir, "entry.png");

function sha256(file: string): string {
  return crypto.createHash("sha256").update(fs.readFileSync(file)).digest("hex");
}

fs.mkdirSync(outDir, { recursive: true });
fs.copyFileSync(src, dst);
if (sha256(src) !== sha256(dst)) {
  console.error("sha256 mismatch between meme.png and entry.png");
  process.exit(1);
}
console.log("wrote " + dst);

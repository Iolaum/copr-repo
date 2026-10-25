// Local-only v2 setup fixture: no npm dependencies, providers, or model calls.
import { Plugin } from "@opencode/plugin"
import { writeFileSync } from "node:fs"

export default Plugin.define({
  id: "copr.no-bun.fixture",
  setup(ctx) {
    const path = process.env.COPR_NO_BUN_MARKER
    if (!path || !path.startsWith("/home/tester/")) {
      throw new Error("Expected a disposable container marker path")
    }
    writeFileSync(path, JSON.stringify({
      marker: "COPR_NO_BUN_PLUGIN_SETUP_20261025",
      version: ctx.app.version,
    }) + "\n", { flag: "wx" })
  },
})

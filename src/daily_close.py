"""每日收盘轮统一入口（launchd 调用，独立于任何 Claude 会话）。

流程：交易日检查 → TOM sleeve（初始化/换仓/mark）→ 影子仓管理 → 日报 → git commit+push。
全规则型，无 LLM 依赖。收盘后任何时刻执行均正确（基于日线收盘价）。
日志：logs/daily_YYYYMMDD.log
"""
import subprocess
import sys
import traceback
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
ET = ZoneInfo("America/New_York")

from tom_sleeve import HOLIDAYS  # noqa: E402


def is_trading_day(d):
    return d.weekday() < 5 and d.strftime("%Y-%m-%d") not in HOLIDAYS


def sh(cmd):
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=ROOT, timeout=600)
    return r.stdout + r.stderr


def main():
    now = datetime.now(ET)
    log = [f"=== daily_close {now.isoformat(timespec='seconds')} ==="]
    if not is_trading_day(now):
        log.append("non-trading day, exit")
    else:
        for name, script in [("TOM", "tom_sleeve.py"), ("IEF", "ief_sleeve.py"), ("SVXY", "svxy_sleeve.py"), ("H6", "h6_sleeve.py"), ("POSITIONS", "manage_positions.py"), ("REPORT", "report.py")]:
            try:
                out = sh(f".venv/bin/python src/{script}")
                log.append(f"--- {name} ---\n{out.strip()}")
            except Exception:  # noqa: BLE001
                log.append(f"--- {name} FAILED ---\n{traceback.format_exc()}")
        try:
            sh("git add -A")
            day = now.strftime("%Y-%m-%d")
            sh(f'git -c user.name=alphatrade-agent -c user.email=ralph.wen@gmail.com commit -q -m "daily close {day} (auto)"')
            log.append("--- GIT ---\n" + sh("git -c pull.rebase=true pull -q origin main 2>&1; git push -q origin main 2>&1 || echo push-failed"))
        except Exception:  # noqa: BLE001
            log.append("--- GIT FAILED ---\n" + traceback.format_exc())
    logdir = ROOT / "logs"
    logdir.mkdir(exist_ok=True)
    (logdir / f"daily_{now.strftime('%Y%m%d')}.log").write_text("\n".join(log))
    print("\n".join(log))


if __name__ == "__main__":
    main()

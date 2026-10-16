"""Exercise the installed wheel's actual console entry point outside this checkout."""
import hashlib, json, os, pathlib, shutil, sqlite3, subprocess, sys, tempfile

SOURCE=pathlib.Path(__file__).absolute().parent
PYTHON=pathlib.Path(sys.argv[1]).absolute()  # Do not resolve a venv symlink to its base interpreter.
COMMAND=PYTHON.parent / ("gpx-dwell-report.exe" if os.name=="nt" else "gpx-dwell-report")
CASES=0
def run(args, expected=0, data=True):
    global CASES
    p=subprocess.run([str(COMMAND), *map(str,args)],cwd=WORK,text=True,capture_output=True,timeout=30)
    assert p.returncode==expected, (args,p.returncode,p.stdout,p.stderr)
    CASES+=1
    if expected==2:
        assert not p.stdout and p.stderr, (args,p.stdout,p.stderr)
        return None
    return json.loads(p.stdout) if data else p.stdout

with tempfile.TemporaryDirectory(prefix="installed-command-") as tmp:
    WORK=pathlib.Path(tmp)
    assert not WORK.is_relative_to(SOURCE)
    env=subprocess.run([str(PYTHON),"-c","import gpx_dwell_report; print(gpx_dwell_report.__file__)"],cwd=WORK,text=True,capture_output=True,check=True)
    installed=pathlib.Path(env.stdout.strip()).absolute()
    assert not installed.is_relative_to(SOURCE), installed
    assert installed.read_bytes()==(SOURCE/"gpx_dwell_report.py").read_bytes()
    run(["--help"],data=False)
    shutil.copyfile(SOURCE/"example.gpx",WORK/"example.gpx")
    raw=(WORK/"example.gpx").read_text();r=run(["example.gpx"])
    assert r["dwell_seconds"]==120 and len(r["dwell_windows"])==1 and not r["findings"]
    r=run(["example.gpx","--max-gap-s","30"],1);assert len(r["findings"])==3 and r["dwell_seconds"]==0
    r=run(["example.gpx","--max-speed-mps","0.1"],1);assert r["findings"][0]["reasons"]==["speed_jump"]
    for bad in ('<!DOCTYPE gpx [<!ENTITY x "hello">]>'+raw,raw.replace('2026-01-01T00:01:00Z','invalid'),raw.replace('lat="0"','lat="100"')):
        (WORK/"bad.gpx").write_text(bad);run(["bad.gpx"],2)
    run(["example.gpx","--radius-m","nan"],2)
    (WORK/"bad.gpx").write_bytes(b"x"*(2*1024*1024+1));run(["bad.gpx"],2)
print(json.dumps({"installed_command":"gpx-dwell-report","cases":CASES,"module_bytes_match_source":True,"outside_checkout":True,"python":subprocess.check_output([str(PYTHON),"--version"],text=True).strip()}))

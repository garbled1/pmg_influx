# pmg_influx
Proxmox Mail Gateway (pmg) influxdb feeder

Note: Needs git version pf proxmoxer to work.

Example installation:

```
python3 -m venv destdir
source destdir/bin/activate
git clone https://github.com/proxmoxer/proxmoxer.git
cd proxmoxer/
python3 ./setup.py install
cd ..
git clone https://github.com/garbled1/pmg_influx.git
cd pmg_influx/
python3 ./setup.py install
cd ..

destdir/bin/pmg_influx -i influx_host --host pmg_host --user influx@pmg --password secret
```

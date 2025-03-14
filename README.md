# libre-hardware-exporter
Prometheus exporter for Libre Hardware Monitor

# What is this repo doing?
You are able to export all Libre Hardware Monitor Data to Prometheus, or also your FPS from Riva Tuner Statistics, or both.

# Requirements
- Python
- nssm
- Libre Hardware Monitor

__Optional__
- Riva Tuner Statistics
- MSI Afterburner

# What's inside?
- `fps_exporter.py`
- - exports fps from Riva Tuner Statistics (MSI Afterburner required)
- `libre-exporter.py`
- - exports all data from Libre Hardware Monitor (Remote logging required)
- `combined_exporter.py`
- - Combines both directly

# Installation

1. Make sure to make your firewall clearing ready (Powershell with Adminrights needed here):
   * `New-NetFirewallRule -DisplayName "Allow Libre Hardware Monitor API" -Direction Inbound -LocalPort 9187 -Protocol TCP -Action Allow`
   * The same needs to be done, if you want to have both exporter running at the same time, but on a differnt port.
  
2. Make sure to find a good location for the scripts and download them from this repository. __(For example C:/tooling/dashboarding)__
3. Get __[NSSM]([https://www.google.com](https://nssm.cc/download))__ from "latest release"
   * The easiest way

5. Prometheus configuration file (prometheus.yaml):

``` yaml
scrape_configs:
  - job_name: 'libre_exporter'
    static_configs:
      - targets: ['$YOUR.GAMING.MACHINE.IP:9187']
```
5. 

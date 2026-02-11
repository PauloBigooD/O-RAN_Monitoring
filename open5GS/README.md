<div style="display: flex; align-items: center;">
  <img src="https://open5gs.org/assets/img/open5gs-logo.png" width="280px">
</div>

---
More info here: <https://docs.docker.com/compose/networking/>

## Advanced Usage

### Open5GS Container Parameters

Advanced parameters for the Open5GS container are stored in [open5gs.env](open5gs/open5gs.env) file. You can modify it or use a totally different file by setting `OPEN_5GS_ENV_FILE` variable like in:

```bash
OPEN_5GS_ENV_FILE=open5gs/open5gs.env docker compose -f docker-compose.yml up 5gc -d
```

The following parameters can be set:

- MONGODB_IP (default: 127.0.0.1): This is the IP of the mongodb to use. 127.0.0.1 is the mongodb that runs inside this container.
- SUBSCRIBER_DB (default: "001010123456780,00112233445566778899aabbccddeeff,opc,63bfa50ee6523365ff14c1f45f88737d,8000,10.45.1.2"): This adds subscriber data for a single or multiple users to the Open5GS mongodb. It contains either:
  - Comma separated string with information to define a subscriber
  - `subscriber_db.csv`. This is a csv file that contains entries to add to open5gs mongodb. Each entry will represent a subscriber. It must be stored in `srsgnb/docker/open5gs/`
- OPEN5GS_IP: This must be set to the IP of the container (here: 10.53.1.2).
- UE_IP_BASE: Defines the IP base used for connected UEs (here: 10.45.0).
- DEBUG (default: false): This can be set to true to run Open5GS in debug mode.

For more info, please check it's own [README.md](open5gs/README.md).

### Open5GS Container Applications

Open5Gs container includes other binaries such as

- 5gc: 5G Core Only
- epc: EPC Only
- app: Both 5G Core and EPC

By default 5gc is launched. If you want to run another binary, remember you can use `docker compose run` to run any command inside the container. For example:

```bash
docker compose -f docker/docker-compose.yml run 5gc epc -c open5gs-5gc.yml -d
```

If you need to use custom configuration files, remember you can share folder and files between your local PC (host) and the container:

```bash
docker compose -f docker/docker-compose.yml run -v /tmp/my-open5gs-5gc.yml:/config/my-open5gs-5gc.yml 5gc epc -c /config/my-open5gs-5gc.yml -d
```

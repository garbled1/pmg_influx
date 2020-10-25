#!/usr/bin/env python3

import time
from influxdb import InfluxDBClient
from proxmoxer import ProxmoxAPI
import argparse


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", help="Hostname of PMG",
                        required=True)
    parser.add_argument("--user", help="PMG Username", default="root@pam")
    parser.add_argument("--password", help="PMG Password", default="1234")
    parser.add_argument('-i', '--influx_host', type=str, action='store',
                        default='127.0.0.1',
                        help='hostname of influx db (127.0.0.1)')
    parser.add_argument('-p', '--influx_port', type=int, action='store',
                        default=8086,
                        help='port number of influx db (8086)')
    parser.add_argument('--influx_user', type=str, action='store',
                        default=None,
                        help='InfluxDB username')
    parser.add_argument('--influx_pass', type=str, action='store',
                        default=None,
                        help='InfluxDB password')
    parser.add_argument('-d', '--influx_db', type=str, action='store',
                        default='pmg',
                        help='InfluxDB database name (default: pmg)')
    parser.add_argument('--poll_time', type=int, action='store',
                        default=60,
                        help='How often in seconds to poll pmg (60)')

    args = parser.parse_args()
    return args


def gather_domains(pmg, pmg_host):
    dstats = pmg.statistics.domains.get()

    influx_json = []
    now = round(time.time())

    for idx, input in enumerate(dstats):
        domain = input.pop('domain')
        point = {
            "measurement": "domains",
            "time": now,
            "tags": {
                "domain": domain,
                "host": pmg_host,
            },
            "fields": input
        }
        influx_json.append(point)
    return(influx_json)


def gather_mail(pmg, pmg_host):
    dstats = pmg.statistics.mail.get()

    influx_json = []
    now = round(time.time())

    point = {
        "measurement": "mail",
        "time": now,
        "tags": {
            "host": pmg_host,
        },
        "fields": dstats
    }
    influx_json.append(point)
    return(influx_json)


def gather_mailcount(pmg, pmg_host):
    dstats = pmg.statistics.mailcount.get()

    influx_json = []

    for idx, input in enumerate(dstats):
        nowtime = input.pop('time')
        input.pop('index')
        point = {
            "measurement": "mailcount",
            "time": nowtime,
            "tags": {
                "host": pmg_host,
            },
            "fields": input
        }
        influx_json.append(point)
    return(influx_json)


def gather_recent(pmg, pmg_host):
    dstats = pmg.statistics.recent.get()

    influx_json = []

    for idx, input in enumerate(dstats):
        nowtime = input.pop('time')
        input.pop('index')
        input.pop('timespan')
        input['ptimesum'] = float(input['ptimesum'])
        point = {
            "measurement": "recent",
            "time": nowtime,
            "tags": {
                "host": pmg_host,
            },
            "fields": input
        }
        influx_json.append(point)
    return(influx_json)


def gather_spamscores(pmg, pmg_host):
    dstats = pmg.statistics.spamscores.get()

    influx_json = []
    nowtime = round(time.time())

    for idx, input in enumerate(dstats):
        level = input.pop('level')
        input['ratio'] = float(input['ratio'])
        point = {
            "measurement": "spamscores",
            "time": nowtime,
            "tags": {
                "level": str(level),
                "host": pmg_host,
            },
            "fields": input
        }
        influx_json.append(point)
    return(influx_json)


def gather_virus(pmg, pmg_host):
    dstats = pmg.statistics.virus.get()

    influx_json = []
    nowtime = round(time.time())

    for idx, input in enumerate(dstats):
        name = input.pop('name')
        point = {
            "measurement": "virus",
            "time": nowtime,
            "tags": {
                "name": name,
                "host": pmg_host,
            },
            "fields": input
        }
        influx_json.append(point)
    return(influx_json)


def main(args=None):
    args = parse_arguments()

    try:
        if args.influx_user and args.influx_pass:
            db_client = InfluxDBClient(host=args.influx_host,
                                       port=args.influx_port,
                                       username=args.influx_user,
                                       password=args.influx_pass)
        else:
            db_client = InfluxDBClient(host=args.influx_host,
                                       port=args.influx_port)
    except Exception as e:
        print("Cannot connect to InfluxDB!")
        print(e)
        return(1)

    try:
        db_client.switch_database(args.influx_db)
    except Exception as e:
        print("Cannot find db named {0}, please create".format(args.influx_db))
        print(e)
        return(1)

    try:
        pmg = ProxmoxAPI(args.host, user=args.user, password=args.password,
                         verify_ssl=False, service='PMG')
    except Exception as e:
        print("Cannot connect to PMG:")
        print(e)
        return(1)

    gather_list = [
        gather_domains,
        gather_mail,
        gather_mailcount,
        gather_recent,
        gather_spamscores,
        gather_virus
    ]

    while (True):
        for gfunc in gather_list:
            influxdata = gfunc(pmg, args.host)
            # print(gfunc)
            try:
                db_client.write_points(influxdata, time_precision='s')
            except Exception as e:
                print("Cannot contact influx: {0}".format(str(e)))
                exit(1)
            time.sleep(args.poll_time)


if __name__ == "__main__":
    main()

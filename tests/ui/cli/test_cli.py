# -*- coding: utf-8 -*-
# Copyright (C) 2018-2021, earthobservations developers.
# Distributed under the MIT License. See LICENSE for more info.
import json

import pytest
from click.testing import CliRunner
from dirty_equals import IsStr

from wetterdienst.ui.cli import cli

# Individual settings for observation and mosmix


def test_cli_help():
    """Test cli help"""
    runner = CliRunner()
    result = runner.invoke(cli, [])
    assert "Options:\n --help  Show this message and exit."
    assert (
        "Basic:\n"
        "  cache\n"
        "  info\n"
        "\n"
        "Advanced:\n"
        "  restapi\n"
        "  explorer\n"
        "\n"
        "Data:\n"
        "  about\n"
        "  stations\n"
        "  values\n"
        "  interpolate\n"
        "  summarize\n"
        "  radar\n" in result.output
    )


def test_cli_about_parameters():
    """Test cli coverage of dwd parameters"""
    runner = CliRunner()
    result = runner.invoke(cli, "about coverage --provider=dwd --network=observation")
    assert "precipitation" in result.output
    assert "temperature_air" in result.output
    assert "weather_phenomena" in result.output


def test_cli_about_resolutions():
    """Test cli coverage of dwd resolutions"""
    runner = CliRunner()
    result = runner.invoke(cli, "about coverage --provider=dwd --network=observation")
    assert "minute_1" in result.output
    assert "hourly" in result.output
    assert "annual" in result.output


def test_cli_about_coverage(capsys):
    runner = CliRunner()
    result = runner.invoke(cli, "about coverage --provider=dwd --network=observation")
    assert "minute_1" in result.output
    assert "precipitation" in result.output


def test_no_provider():
    runner = CliRunner()
    result = runner.invoke(cli, "stations --provider=abc --network=abc")
    assert (
        "Error: Invalid value for '--provider': 'abc' is not one of 'DWD', 'EA', 'EAUFRANCE', 'ECCC', 'GEOSPHERE', "
        "'IMGW', 'NOAA', 'NWS', 'WSV'" in result.output
    )


def test_no_network(caplog):
    runner = CliRunner()
    runner.invoke(
        cli, "stations --provider=dwd --network=abc --parameter=precipitation_height --resolution=daily --all"
    )
    assert "No API available for provider DWD and network abc" in caplog.text


@pytest.mark.remote
def test_cli_interpolate():
    runner = CliRunner()
    result = runner.invoke(
        cli,
        "interpolate --provider=dwd --network=observation "
        "--parameter=temperature_air_mean_200 --resolution=daily "
        "--station=00071 --date=1986-10-31/1986-11-01 --format=json",
    )
    if result.exit_code != 0:
        raise ChildProcessError(result.stderr)
    response = json.loads(result.stdout)
    assert response.keys() == {"values"}
    assert response["values"] == [
        {
            "station_id": "6754d04d",
            "parameter": "temperature_air_mean_200",
            "date": "1986-10-31T00:00:00+00:00",
            "value": 279.52,
            "distance_mean": 16.99,
            "taken_station_ids": ["00072", "02074", "02638", "04703"],
        },
        {
            "station_id": "6754d04d",
            "parameter": "temperature_air_mean_200",
            "date": "1986-11-01T00:00:00+00:00",
            "value": 281.85,
            "distance_mean": 0.0,
            "taken_station_ids": ["00071"],
        },
    ]


@pytest.mark.remote
def test_cli_interpolate_with_metadata_with_stations(metadata):
    runner = CliRunner()
    result = runner.invoke(
        cli,
        "interpolate --provider=dwd --network=observation "
        "--parameter=temperature_air_mean_200 --resolution=daily "
        "--station=00071 --date=1986-10-31/1986-11-01 --format=json --with-metadata=true --with-stations=true",
    )
    if result.exit_code != 0:
        raise ChildProcessError(result.stderr)
    response = json.loads(result.stdout)
    assert response.keys() == {"metadata", "stations", "values"}
    assert response["metadata"] == metadata
    assert response["stations"] == [
        {
            "station_id": "00071",
            "start_date": "1986-11-01T00:00:00+00:00",
            "end_date": "2019-12-31T00:00:00+00:00",
            "latitude": 48.2156,
            "longitude": 8.9784,
            "height": 759.0,
            "name": "Albstadt-Badkap",
            "state": "Baden-Württemberg",
        },
        {
            "station_id": "00072",
            "start_date": "1978-09-01T00:00:00+00:00",
            "end_date": "1995-05-31T00:00:00+00:00",
            "latitude": 48.2766,
            "longitude": 9.0001,
            "height": 794.0,
            "name": "Albstadt-Onstmettingen",
            "state": "Baden-Württemberg",
        },
        {
            "station_id": "02074",
            "start_date": "1947-01-01T00:00:00+00:00",
            "end_date": IsStr,
            "latitude": 48.3752,
            "longitude": 8.98,
            "height": 518.0,
            "name": "Hechingen",
            "state": "Baden-Württemberg",
        },
        {
            "station_id": "02638",
            "start_date": "1947-01-01T00:00:00+00:00",
            "end_date": IsStr,
            "latitude": 48.1054,
            "longitude": 8.7548,
            "height": 974.0,
            "name": "Klippeneck",
            "state": "Baden-Württemberg",
        },
        {
            "station_id": "04703",
            "start_date": "1951-01-01T00:00:00+00:00",
            "end_date": IsStr,
            "latitude": 48.0719,
            "longitude": 9.1943,
            "height": 581.0,
            "name": "Sigmaringen-Laiz",
            "state": "Baden-Württemberg",
        },
    ]


@pytest.mark.remote
def test_cli_interpolate_geojson():
    runner = CliRunner()
    result = runner.invoke(
        cli,
        "interpolate --provider=dwd --network=observation "
        "--parameter=temperature_air_mean_200 --resolution=daily "
        "--station=00071 --date=1986-10-31/1986-11-01 --format=geojson",
    )
    if result.exit_code != 0:
        raise ChildProcessError(result.stderr)
    response = json.loads(result.stdout)
    assert response.keys() == {"data"}
    assert response["data"] == {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": {"id": "6754d04d", "name": "interpolation(48.2156,8.9784)"},
                "geometry": {"type": "Point", "coordinates": [8.9784, 48.2156]},
                "stations": [
                    {
                        "station_id": "00071",
                        "start_date": "1986-11-01T00:00:00+00:00",
                        "end_date": "2019-12-31T00:00:00+00:00",
                        "latitude": 48.2156,
                        "longitude": 8.9784,
                        "height": 759.0,
                        "name": "Albstadt-Badkap",
                        "state": "Baden-Württemberg",
                    },
                    {
                        "station_id": "00072",
                        "start_date": "1978-09-01T00:00:00+00:00",
                        "end_date": "1995-05-31T00:00:00+00:00",
                        "latitude": 48.2766,
                        "longitude": 9.0001,
                        "height": 794.0,
                        "name": "Albstadt-Onstmettingen",
                        "state": "Baden-Württemberg",
                    },
                    {
                        "station_id": "02074",
                        "start_date": "1947-01-01T00:00:00+00:00",
                        "end_date": IsStr,
                        "latitude": 48.3752,
                        "longitude": 8.98,
                        "height": 518.0,
                        "name": "Hechingen",
                        "state": "Baden-Württemberg",
                    },
                    {
                        "station_id": "02638",
                        "start_date": "1947-01-01T00:00:00+00:00",
                        "end_date": IsStr,
                        "latitude": 48.1054,
                        "longitude": 8.7548,
                        "height": 974.0,
                        "name": "Klippeneck",
                        "state": "Baden-Württemberg",
                    },
                    {
                        "station_id": "04703",
                        "start_date": "1951-01-01T00:00:00+00:00",
                        "end_date": IsStr,
                        "latitude": 48.0719,
                        "longitude": 9.1943,
                        "height": 581.0,
                        "name": "Sigmaringen-Laiz",
                        "state": "Baden-Württemberg",
                    },
                ],
                "values": [
                    {
                        "station_id": "6754d04d",
                        "parameter": "temperature_air_mean_200",
                        "date": "1986-10-31T00:00:00+00:00",
                        "value": 279.52,
                        "distance_mean": 16.99,
                        "taken_station_ids": ["00072", "02074", "02638", "04703"],
                    },
                    {
                        "station_id": "6754d04d",
                        "date": "1986-11-01T00:00:00+00:00",
                        "parameter": "temperature_air_mean_200",
                        "value": 281.85,
                        "distance_mean": 0.0,
                        "taken_station_ids": ["00071"],
                    },
                ],
            }
        ],
    }


@pytest.mark.remote
def test_cli_summarize():
    runner = CliRunner()
    result = runner.invoke(
        cli,
        "summarize --provider=dwd --network=observation "
        "--parameter=temperature_air_mean_200 --resolution=daily "
        "--station=00071 --date=1986-10-31/1986-11-01 --format=json",
    )
    if result.exit_code != 0:
        raise ChildProcessError(result.stderr)
    response = json.loads(result.stdout)
    assert response.keys() == {"values"}
    assert response["values"] == [
        {
            "station_id": "a87291a8",
            "parameter": "temperature_air_mean_200",
            "date": "1986-10-31T00:00:00+00:00",
            "value": 279.75,
            "distance": 6.97,
            "taken_station_id": "00072",
        },
        {
            "station_id": "a87291a8",
            "parameter": "temperature_air_mean_200",
            "date": "1986-11-01T00:00:00+00:00",
            "value": 281.85,
            "distance": 0.0,
            "taken_station_id": "00071",
        },
    ]


@pytest.mark.remote
def test_cli_summarize_geojson():
    runner = CliRunner()
    result = runner.invoke(
        cli,
        "summarize --provider=dwd --network=observation "
        "--parameter=temperature_air_mean_200 --resolution=daily "
        "--station=00071 --date=1986-10-31/1986-11-01 --format=geojson",
    )
    if result.exit_code != 0:
        raise ChildProcessError(result.stderr)
    response = json.loads(result.stdout)
    assert response.keys() == {"data"}
    assert response["data"] == {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": {"id": "a87291a8", "name": "summary(48.2156,8.9784)"},
                "geometry": {"type": "Point", "coordinates": [8.9784, 48.2156]},
                "stations": [
                    {
                        "station_id": "00071",
                        "start_date": "1986-11-01T00:00:00+00:00",
                        "end_date": "2019-12-31T00:00:00+00:00",
                        "latitude": 48.2156,
                        "longitude": 8.9784,
                        "height": 759.0,
                        "name": "Albstadt-Badkap",
                        "state": "Baden-Württemberg",
                    },
                    {
                        "station_id": "00072",
                        "start_date": "1978-09-01T00:00:00+00:00",
                        "end_date": "1995-05-31T00:00:00+00:00",
                        "latitude": 48.2766,
                        "longitude": 9.0001,
                        "height": 794.0,
                        "name": "Albstadt-Onstmettingen",
                        "state": "Baden-Württemberg",
                    },
                ],
                "values": [
                    {
                        "station_id": "a87291a8",
                        "parameter": "temperature_air_mean_200",
                        "date": "1986-10-31T00:00:00+00:00",
                        "value": 279.75,
                        "distance": 6.97,
                        "taken_station_id": "00072",
                    },
                    {
                        "station_id": "a87291a8",
                        "parameter": "temperature_air_mean_200",
                        "date": "1986-11-01T00:00:00+00:00",
                        "value": 281.85,
                        "distance": 0.0,
                        "taken_station_id": "00071",
                    },
                ],
            }
        ],
    }


def test_cli_radar_stations_opera():
    runner = CliRunner()
    result = runner.invoke(cli, "radar --odim-code=ukdea")
    response = json.loads(result.output)
    assert isinstance(response, dict)
    assert response["location"] == "Dean Hill"


def test_cli_radar_stations_dwd():
    runner = CliRunner()
    result = runner.invoke(cli, "radar --dwd")
    response = json.loads(result.output)
    assert isinstance(response, list)
    assert len(response) == 20

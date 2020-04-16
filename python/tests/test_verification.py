import socket

import pytest

from bottica import verification


def test_gethostbyaddr_not_found(mocker):
    def raise_not_found(_):
        raise socket.herror(1, "Not found")

    mock = mocker.patch("socket.gethostbyaddr", side_effect=raise_not_found)
    output = verification._gethostbyaddr("1.2.3.4", max_tries=10)

    assert mock.called_once()  # no retries
    assert output == (None, None, None)


def test_gethostbyaddr_retries(mocker):
    def raise_retry(_):
        raise socket.gaierror(2, "Try again")

    mock = mocker.patch("socket.gethostbyaddr", side_effect=raise_retry)

    with pytest.raises(socket.gaierror):
        verification._gethostbyaddr("1.2.3.4", max_tries=10)

    assert mock.call_count == 10


def test_fcrdns_hosts_host_not_found(mocker):
    mocker.patch("bottica.verification.get_hostname_by_ip", return_value=None)
    verified = verification.fcrdns_hosts("1.2.3.4")
    assert not verified


def test_fcrdns_hosts_ip_not_found(mocker):
    mocker.patch("bottica.verification.get_hostname_by_ip", return_value="google.com")
    mocker.patch("bottica.verification.get_ips_by_hostname", return_value=None)
    verified = verification.fcrdns_hosts("1.2.3.4")
    assert not verified


def test_fcrdns_ip_not_match(mocker):
    mocker.patch("bottica.verification.get_hostname_by_ip", return_value="google.com")
    mocker.patch("bottica.verification.get_ips_by_hostname", return_value=["2.3.4.5"])
    verified = verification.fcrdns_hosts("1.2.3.4")
    assert not verified


def test_fcrdns_host_not_in_list(mocker):
    mocker.patch("bottica.verification.get_hostname_by_ip", return_value="google.com")
    mocker.patch("bottica.verification.get_ips_by_hostname", return_value="1.2.3.4")
    verified = verification.fcrdns_hosts("1.2.3.4", allowed_hosts=["bing.com"])
    assert not verified


def test_fcrdns_host_in_list(mocker):
    mocker.patch("bottica.verification.get_hostname_by_ip", return_value="google.com")
    mocker.patch("bottica.verification.get_ips_by_hostname", return_value="1.2.3.4")
    verified = verification.fcrdns_hosts("1.2.3.4", allowed_hosts=["google.com"])
    assert verified


def test_fcrdns_any_host(mocker):
    mocker.patch("bottica.verification.get_hostname_by_ip", return_value="google.com")
    mocker.patch("bottica.verification.get_ips_by_hostname", return_value="1.2.3.4")
    verified = verification.fcrdns_hosts("1.2.3.4")
    assert verified


@pytest.mark.parametrize(
    "ip, ip_list, verified",
    [
        ("1.2.3.4", ["1.2.3.4", "2.3.4.5"], True),
        ("3.4.5.6", ["1.2.3.4", "2.3.4.5"], False),
    ],
)
def test_ip_list(ip, ip_list, verified):
    assert verification.ip_list(ip, ip_list) == verified


@pytest.mark.parametrize(
    "ip, ip_ranges, verified",
    [
        ("1.2.3.4", [("1.2.3.0", "1.2.3.8")], True),
        ("2.2.3.4", [("1.2.3.0", "1.2.3.8")], False),
        ("1.2.3.4", [("1.2.3.4", "1.2.3.4")], True),
    ],
)
def test_ip_ranges(ip, ip_ranges, verified):
    assert verification.ip_ranges(ip, ip_ranges) == verified


@pytest.mark.parametrize(
    "ip, allowed_cidrs, verified",
    [
        ("1.2.3.4", ["1.2.0.0/16"], True),
        ("2.2.3.4", ["8.8.8.0/24", "2.2.120.0/24"], False),
    ],
)
def test_cidr_list(ip, allowed_cidrs, verified):
    assert verification.cidr_list(ip, allowed_cidrs) == verified

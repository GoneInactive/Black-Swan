use pyo3::prelude::*;
use pyo3::wrap_pyfunction;

mod kraken_api;
use kraken_api::{KrakenClient, KrakenError};

mod binance_api;
use binance_api::{BinanceClient, BinanceError};

fn handle_kraken_result(result: Result<f64, KrakenError>) -> PyResult<f64> {
    match result {
        Ok(value) => Ok(value),
        Err(e) => Err(pyo3::exceptions::PyRuntimeError::new_err(format!("{:?}", e))),
    }
}

fn handle_binance_result<T, E: std::fmt::Debug>(result: Result<T, E>) -> PyResult<T> {
    match result {
        Ok(value) => Ok(value),
        Err(e) => Err(pyo3::exceptions::PyRuntimeError::new_err(format!("{:?}", e))),
    }
}

#[pyfunction]
fn get_bid() -> PyResult<f64> {
    let client = KrakenClient::new();
    handle_kraken_result(client.get_bid())
}

#[pyfunction]
fn get_ask() -> PyResult<f64> {
    let client = KrakenClient::new();
    handle_kraken_result(client.get_ask())
}

#[pyfunction]
fn get_spread() -> PyResult<f64> {
    let client = KrakenClient::new();
    handle_kraken_result(client.get_spread())
}

#[pyfunction]
fn get_balance() -> PyResult<f64> {
    let client = KrakenClient::new();
    handle_kraken_result(client.get_balance())
}

// Binance functions

#[pyfunction]
fn get_binance_depth() -> PyResult<String> {
    let client = BinanceClient::new().map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(format!("{:?}", e)))?;
    let depth = client.get_depth().map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(format!("{:?}", e)))?;
    Ok(serde_json::to_string_pretty(&depth).unwrap_or_default())
}

#[pymodule]
fn rust_kraken_client(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(get_bid, m)?)?;
    m.add_function(wrap_pyfunction!(get_ask, m)?)?;
    m.add_function(wrap_pyfunction!(get_spread, m)?)?;
    m.add_function(wrap_pyfunction!(get_balance, m)?)?;
    m.add_function(wrap_pyfunction!(get_binance_depth, m)?)?;
    Ok(())
}
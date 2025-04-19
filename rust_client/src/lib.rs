use pyo3::prelude::*;
use pyo3::wrap_pyfunction;

mod kraken_api;
use kraken_api::{KrakenClient, KrakenError};

fn handle_result(result: Result<f64, KrakenError>) -> PyResult<f64> {
    match result {
        Ok(value) => Ok(value),
        Err(e) => Err(pyo3::exceptions::PyRuntimeError::new_err(format!("{:?}", e))),
    }
}

#[pyfunction]
fn get_bid() -> PyResult<f64> {
    let client = KrakenClient::new();
    handle_result(client.get_bid())
}

#[pyfunction]
fn get_ask() -> PyResult<f64> {
    let client = KrakenClient::new();
    handle_result(client.get_ask())
}

#[pyfunction]
fn get_spread() -> PyResult<f64> {
    let client = KrakenClient::new();
    handle_result(client.get_spread())
}

#[pyfunction]
fn get_balance() -> PyResult<f64> {
    let client = KrakenClient::new();
    handle_result(client.get_balance())
}

#[pymodule]
fn rust_kraken_client(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(get_bid, m)?)?;
    m.add_function(wrap_pyfunction!(get_ask, m)?)?;
    m.add_function(wrap_pyfunction!(get_spread, m)?)?;
    m.add_function(wrap_pyfunction!(get_balance, m)?)?;
    Ok(())
}

use pyo3::prelude::*;
use pyo3::wrap_pyfunction;
use std::collections::HashMap;

mod kraken;
use kraken::{KrakenClient, KrakenError};
use kraken::account::OrderResponse;
mod binance_api;
use binance_api::BinanceClient;

// Generic error handler for Kraken results
fn handle_kraken_result<T>(result: Result<T, KrakenError>) -> PyResult<T> {
    match result {
        Ok(value) => Ok(value),
        Err(e) => Err(pyo3::exceptions::PyRuntimeError::new_err(format!("{:?}", e))),
    }
}

// Generic error handler for Binance results
fn handle_binance_result<T, E: std::fmt::Debug>(result: Result<T, E>) -> PyResult<T> {
    match result {
        Ok(value) => Ok(value),
        Err(e) => Err(pyo3::exceptions::PyRuntimeError::new_err(format!("{:?}", e))),
    }
}

#[pyclass]
#[derive(Clone)]
pub struct PyOrderResponse {
    #[pyo3(get)]
    pub txid: Vec<String>,
    #[pyo3(get)]
    pub description: String,
}

#[pymethods]
impl PyOrderResponse {
    fn __str__(&self) -> String {
        format!("Order(txid={:?}, description='{}')", self.txid, self.description)
    }
   
    fn __repr__(&self) -> String {
        self.__str__()
    }
}

impl From<OrderResponse> for PyOrderResponse {
    fn from(order: OrderResponse) -> Self {
        PyOrderResponse {
            txid: order.txid,
            description: order.description,
        }
    }
}

#[pyfunction]
fn get_open_orders_raw() -> PyResult<String> {
    let client = KrakenClient::new();
    handle_kraken_result(client.get_open_orders_raw())
}

#[pyfunction]
fn cancel_order(txid: String) -> PyResult<bool> {
    let client = KrakenClient::new();
    handle_kraken_result(client.cancel_order(&txid))
}

#[pyfunction]
fn get_bid(pair: String) -> PyResult<f64> {
    let client = KrakenClient::new();
    handle_kraken_result(client.get_bid(&pair))
}

#[pyfunction]
fn get_ask(pair: String) -> PyResult<f64> {
    let client = KrakenClient::new();
    handle_kraken_result(client.get_ask(&pair))
}

#[pyfunction]
fn get_spread(pair: String) -> PyResult<f64> {
    let client = KrakenClient::new();
    handle_kraken_result(client.get_spread(&pair))
}

#[pyfunction]
fn get_balance() -> PyResult<HashMap<String, f64>> {
    let client = KrakenClient::new();
    handle_kraken_result(client.get_balance())
}

#[pyfunction]
fn add_order(pair: String, side: String, price: f64, volume: f64) -> PyResult<PyOrderResponse> {
    let client = KrakenClient::new();
    handle_kraken_result(client.add_order(&pair, &side, price, volume))
        .map(PyOrderResponse::from)
}

#[pyfunction]
fn get_recent_trades(ticker: String) -> PyResult<Vec<(f64, f64, f64, String, String, String)>> {
    let client = KrakenClient::new();
    handle_kraken_result(client.get_recent_trades(&ticker))
}

#[pyfunction]
fn get_orderbook(pair: String) -> PyResult<(Vec<f64>, Vec<f64>)> {
    let client = KrakenClient::new();
    handle_kraken_result(client.get_orderbook(&pair))
}

#[pyfunction]
fn get_binance_depth() -> PyResult<String> {
    let client = BinanceClient::new()
        .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(format!("{:?}", e)))?;
    let depth = client.get_depth()
        .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(format!("{:?}", e)))?;
    Ok(serde_json::to_string_pretty(&depth).unwrap_or_default())
}

#[pyfunction]
fn edit_order(
    txid: String,
    pair: String,
    side: String,
    price: f64,
    volume: f64,
    new_userref: Option<String>,
) -> PyResult<PyOrderResponse> {
    let client = KrakenClient::new();
    handle_kraken_result(client.edit_order(&txid, &pair, &side, price, volume, new_userref.as_deref()))
        .map(PyOrderResponse::from)
}

#[pymodule]
fn rust_kraken_client(_py: Python<'_>, m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(get_open_orders_raw, m)?)?;
    m.add_function(wrap_pyfunction!(cancel_order, m)?)?;
    m.add_function(wrap_pyfunction!(get_bid, m)?)?;
    m.add_function(wrap_pyfunction!(get_ask, m)?)?;
    m.add_function(wrap_pyfunction!(get_spread, m)?)?;
    m.add_function(wrap_pyfunction!(get_balance, m)?)?;
    m.add_function(wrap_pyfunction!(add_order, m)?)?;
    m.add_function(wrap_pyfunction!(get_recent_trades, m)?)?;
    m.add_function(wrap_pyfunction!(get_orderbook, m)?)?;
    m.add_function(wrap_pyfunction!(get_binance_depth, m)?)?;
    m.add_function(wrap_pyfunction!(edit_order, m)?)?;
    m.add_class::<PyOrderResponse>()?;
    Ok(())
}
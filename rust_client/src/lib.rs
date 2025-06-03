use pyo3::prelude::*;
use pyo3::wrap_pyfunction;
use std::collections::HashMap;
mod kraken_api;
use kraken_api::{KrakenClient, KrakenError, OrderResponse};
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

// Python class to represent order response
#[pyclass]
#[derive(Clone)]
pub struct PyOrderResponse {
    #[pyo3(get)]
    pub txid: Vec<String>,
    #[pyo3(get)]
    pub description: String,
}

#[pyclass]
#[derive(Clone)]
pub struct PyOrderDescription {
    #[pyo3(get)]
    pub pair: String,
    #[pyo3(get, name = "type")]
    pub order_type: String,
    #[pyo3(get)]
    pub ordertype: String,
    #[pyo3(get)]
    pub price: String,
    #[pyo3(get)]
    pub price2: String,
    #[pyo3(get)]
    pub leverage: String,
    #[pyo3(get)]
    pub order: String,
    #[pyo3(get)]
    pub close: Option<String>,
}


#[pyclass]
#[derive(Clone)]
pub struct PyOpenOrder {
    #[pyo3(get)]
    pub refid: Option<String>,
    #[pyo3(get)]
    pub userref: Option<String>,
    #[pyo3(get)]
    pub status: String,
    #[pyo3(get)]
    pub opentm: f64,
    #[pyo3(get)]
    pub starttm: f64,
    #[pyo3(get)]
    pub expiretm: f64,
    #[pyo3(get)]
    pub descr: PyOrderDescription,
    #[pyo3(get)]
    pub vol: f64,
    #[pyo3(get)]
    pub vol_exec: f64,
    #[pyo3(get)]
    pub cost: f64,
    #[pyo3(get)]
    pub fee: f64,
    #[pyo3(get)]
    pub price: f64,
    #[pyo3(get)]
    pub stopprice: f64,
    #[pyo3(get)]
    pub limitprice: f64,
    #[pyo3(get)]
    pub misc: String,
    #[pyo3(get)]
    pub oflags: String,
    #[pyo3(get)]
    pub reason: Option<String>,
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
    let order_result = client.add_order(&pair, &side, price, volume);
    let order_response = handle_kraken_result(order_result)?;
    Ok(PyOrderResponse::from(order_response))
}


#[pyfunction]
fn get_binance_depth() -> PyResult<String> {
    let client = BinanceClient::new()
        .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(format!("{:?}", e)))?;
    let depth = client.get_depth()
        .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(format!("{:?}", e)))?;
    Ok(serde_json::to_string_pretty(&depth).unwrap_or_default())
}

#[pymodule]
fn rust_kraken_client(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(get_bid, m)?)?;
    m.add_function(wrap_pyfunction!(get_ask, m)?)?;
    m.add_function(wrap_pyfunction!(get_spread, m)?)?;
    m.add_function(wrap_pyfunction!(get_balance, m)?)?;
    m.add_function(wrap_pyfunction!(add_order, m)?)?;
    m.add_function(wrap_pyfunction!(get_binance_depth, m)?)?;
    m.add_function(wrap_pyfunction!(get_open_orders_raw, m)?)?;
    m.add_function(wrap_pyfunction!(cancel_order, m)?)?;
    Ok(())
}
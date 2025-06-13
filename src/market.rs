use std::collections::HashMap;
use serde::Deserialize;
use reqwest::Client;

#[derive(Debug)]
pub struct MarketError {
    pub message: String,
}

impl From<reqwest::Error> for MarketError {
    fn from(error: reqwest::Error) -> Self {
        MarketError {
            message: error.to_string(),
        }
    }
}

pub struct Market {
    client: Client,
}

impl Market {
    pub fn new() -> Self {
        Market {
            client: Client::new(),
        }
    }

    pub fn get_orderbook(&self, pair: &str) -> Result<(Vec<f64>, Vec<f64>), MarketError> {
        let url = format!(
            "https://api.kraken.com/0/public/Depth?pair={}&count=100",
            pair
        );

        let response = self.client.get(&url).send()?;
        let json: serde_json::Value = response.json()?;

        if let Some(result) = json["result"].as_object() {
            let pair_data = result.values().next()
                .ok_or_else(|| MarketError { message: "Missing pair data".to_string() })?;

            let bids = pair_data["bids"].as_array()
                .ok_or_else(|| MarketError { message: "Missing bids".to_string() })?
                .iter()
                .filter_map(|bid| {
                    let price = bid[0].as_str()?.parse::<f64>().ok()?;
                    let volume = bid[1].as_str()?.parse::<f64>().ok()?;
                    Some(price * volume)
                })
                .collect();

            let asks = pair_data["asks"].as_array()
                .ok_or_else(|| MarketError { message: "Missing asks".to_string() })?
                .iter()
                .filter_map(|ask| {
                    let price = ask[0].as_str()?.parse::<f64>().ok()?;
                    let volume = ask[1].as_str()?.parse::<f64>().ok()?;
                    Some(price * volume)
                })
                .collect();

            Ok((bids, asks))
        } else {
            Err(MarketError { message: "Missing result field".to_string() })
        }
    }
} 
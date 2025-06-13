use crate::kraken::{KrakenClient, KrakenError};
use std::collections::HashMap;
use serde::Deserialize;

fn deserialize_number_from_string<'de, D>(deserializer: D) -> Result<f64, D::Error>
where
    D: serde::Deserializer<'de>,
{
    #[derive(Deserialize)]
    #[serde(untagged)]
    enum StringOrFloat {
        String(String),
        Float(f64),
    }

    let value = StringOrFloat::deserialize(deserializer)?;
    match value {
        StringOrFloat::String(s) => s.parse().map_err(serde::de::Error::custom),
        StringOrFloat::Float(f) => Ok(f),
    }
}

impl KrakenClient {
    fn get_ticker(&self, pair: &str) -> Result<HashMap<String, serde_json::Value>, KrakenError> {
        let url = format!(
            "https://api.kraken.com/0/public/Ticker?pair={}",
            pair
        );

        let response = self
            .client
            .get(&url)
            .send()
            .map_err(KrakenError::HttpError)?;

        let json: serde_json::Value = response.json().map_err(|e| {
            KrakenError::ParseError(format!("Failed to parse JSON: {}", e.to_string()))
        })?;

        if let Some(result) = json["result"].as_object() {
            let mut result_map = HashMap::new();
            for (key, value) in result.iter() {
                result_map.insert(key.clone(), value.clone());
            }
            Ok(result_map)
        } else {
            Err(KrakenError::ParseError("Missing result field".into()))
        }
    }

    pub fn get_bid(&self, pair: &str) -> Result<f64, KrakenError> {
        let data = self.get_ticker(pair)?;
        let pair_data = data.values().next().ok_or_else(|| KrakenError::ParseError("Missing pair data".to_string()))?;
        
        let bid = pair_data["b"][0]
            .as_str()
            .ok_or_else(|| KrakenError::ParseError("Missing bid".into()))?;
        
        Ok(bid.parse().unwrap_or(0.0))
    }

    pub fn get_ask(&self, pair: &str) -> Result<f64, KrakenError> {
        let data = self.get_ticker(pair)?;
        let pair_data = data.values().next().ok_or_else(|| KrakenError::ParseError("Missing pair data".to_string()))?;
        
        let ask = pair_data["a"][0]
            .as_str()
            .ok_or_else(|| KrakenError::ParseError("Missing ask".into()))?;
        
        Ok(ask.parse().unwrap_or(0.0))
    }

    pub fn get_spread(&self, pair: &str) -> Result<f64, KrakenError> {
        let bid = self.get_bid(pair)?;
        let ask = self.get_ask(pair)?;
        Ok(ask - bid)
    }

    pub fn get_recent_trades(&self, _ticker: &str) -> Result<Vec<(f64, f64, f64, String, String, String)>, KrakenError> {
        // Implementation would go here
        unimplemented!()
    }

    pub fn get_orderbook(&self, pair: &str) -> Result<(Vec<f64>, Vec<f64>), KrakenError> {
        let data = self.get_ticker(pair)?;
        let pair_data = data.values().next().ok_or_else(|| KrakenError::ParseError("Missing pair data".to_string()))?;
        
        let bids: Vec<f64> = pair_data["b"]
            .as_array()
            .ok_or_else(|| KrakenError::ParseError("Missing bids".into()))?
            .iter()
            .filter_map(|bid| bid.as_str().and_then(|s| s.parse::<f64>().ok()))
            .collect();

        let asks: Vec<f64> = pair_data["a"]
            .as_array()
            .ok_or_else(|| KrakenError::ParseError("Missing asks".into()))?
            .iter()
            .filter_map(|ask| ask.as_str().and_then(|s| s.parse::<f64>().ok()))
            .collect();

        Ok((bids, asks))
    }
}
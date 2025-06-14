use crate::kraken::{KrakenClient, KrakenError};
use serde::Deserialize;
use std::collections::HashMap;

#[derive(Debug)]
pub struct OrderResponse {
    pub txid: Vec<String>,
    pub description: String,
}

#[derive(Debug, Deserialize)]
pub struct OrderDescription {
    pub pair: String,
    #[serde(rename = "type")]
    pub order_type: String,
    pub ordertype: String,
    pub price: String,
    pub price2: String,
    pub leverage: String,
    pub order: String,
    pub close: Option<String>,
}

#[derive(Debug, Deserialize)]
pub struct OpenOrder {
    pub refid: Option<String>,
    pub userref: Option<String>,
    pub status: String,
    #[serde(deserialize_with = "deserialize_f64")]
    pub opentm: f64,
    #[serde(deserialize_with = "deserialize_f64")]
    pub starttm: f64,
    #[serde(deserialize_with = "deserialize_f64")]
    pub expiretm: f64,
    pub descr: OrderDescription,
    #[serde(deserialize_with = "deserialize_f64")]
    pub vol: f64,
    #[serde(deserialize_with = "deserialize_f64")]
    pub vol_exec: f64,
    #[serde(deserialize_with = "deserialize_f64")]
    pub cost: f64,
    #[serde(deserialize_with = "deserialize_f64")]
    pub fee: f64,
    #[serde(deserialize_with = "deserialize_f64")]
    pub price: f64,
    #[serde(deserialize_with = "deserialize_f64")]
    pub stopprice: f64,
    #[serde(deserialize_with = "deserialize_f64")]
    pub limitprice: f64,
    pub misc: String,
    pub oflags: String,
    pub reason: Option<String>,
}

fn deserialize_f64<'de, D>(deserializer: D) -> Result<f64, D::Error>
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
    pub fn get_open_orders_raw(&self) -> Result<String, KrakenError> {
        let nonce = self.generate_nonce();
        let body = format!("nonce={}", nonce);

        let path = "/0/private/OpenOrders";
        let url = format!("https://api.kraken.com{}", path);

        let message = self.create_signature_message(path, &nonce, &body);
        let signature = self.sign_message(&message)?;

        let response = self.client
            .post(&url)
            .header("API-Key", &self.api_key)
            .header("API-Sign", signature)
            .header("Content-Type", "application/x-www-form-urlencoded")
            .body(body)
            .send()
            .map_err(KrakenError::HttpError)?;

        let json_text = response.text()
            .map_err(|e| KrakenError::ParseError(e.to_string()))?;

        Ok(json_text)
    }
    pub fn edit_order(
        &self,
        txid: &str,
        pair: &str,
        side: &str,
        price: f64,
        volume: f64,
        new_userref: Option<&str>,
    ) -> Result<OrderResponse, KrakenError> {
        let side_lower = side.to_lowercase();
        if side_lower != "buy" && side_lower != "sell" {
            return Err(KrakenError::ParseError(
                "Side must be 'buy' or 'sell'".to_string(),
            ));
        }

        let nonce = self.generate_nonce();
        
        let mut params = vec![
            ("nonce".to_string(), nonce.clone()),
            ("ordertype".to_string(), "limit".to_string()),
            ("type".to_string(), side_lower),
            ("volume".to_string(), volume.to_string()),
            ("price".to_string(), price.to_string()),
            ("pair".to_string(), pair.to_string()),
            ("txid".to_string(), txid.to_string()),
        ];

        if let Some(userref) = new_userref {
            params.push(("userref".to_string(), userref.to_string()));
        }

        let body = params
            .iter()
            .map(|(k, v)| format!("{}={}", k, v))
            .collect::<Vec<String>>()
            .join("&");

        let path = "/0/private/EditOrder";
        let url = format!("https://api.kraken.com{}", path);

        let message = self.create_signature_message(path, &nonce, &body);
        let signature = self.sign_message(&message)?;

        let response = self.client
            .post(&url)
            .header("API-Key", &self.api_key)
            .header("API-Sign", signature)
            .header("Content-Type", "application/x-www-form-urlencoded")
            .body(body)
            .send()
            .map_err(KrakenError::HttpError)?;

        let json: serde_json::Value = response.json()
            .map_err(|e| KrakenError::ParseError(e.to_string()))?;

        if let Some(errors) = json.get("error").and_then(serde_json::Value::as_array) {
            if !errors.is_empty() {
                return Err(KrakenError::ParseError(
                    format!("Kraken API error: {:?}", errors)
                ));
            }
        }

        let result = json.get("result")
            .ok_or_else(|| KrakenError::MissingField("result".to_string()))?;

        let txid = result.get("txid")
            .and_then(|t| t.as_array())
            .ok_or_else(|| KrakenError::ParseError("Missing txid array".to_string()))?
            .iter()
            .filter_map(|v| v.as_str().map(|s| s.to_string()))
            .collect::<Vec<String>>();

        let description = result.get("descr")
            .and_then(|d| d.get("order"))
            .and_then(|o| o.as_str())
            .unwrap_or("No description available")
            .to_string();

        Ok(OrderResponse {
            txid,
            description,
        })
    }

    pub fn cancel_order(&self, txid: &str) -> Result<bool, KrakenError> {
        let nonce = self.generate_nonce();
        let body = format!("nonce={}&txid={}", nonce, txid);

        let path = "/0/private/CancelOrder";
        let url = format!("https://api.kraken.com{}", path);

        let message = self.create_signature_message(path, &nonce, &body);
        let signature = self.sign_message(&message)?;

        let response = self.client
            .post(&url)
            .header("API-Key", &self.api_key)
            .header("API-Sign", signature)
            .header("Content-Type", "application/x-www-form-urlencoded")
            .body(body)
            .send()
            .map_err(KrakenError::HttpError)?;

        let json: serde_json::Value = response.json()
            .map_err(|e| KrakenError::ParseError(e.to_string()))?;

        if let Some(errors) = json.get("error").and_then(serde_json::Value::as_array) {
            if !errors.is_empty() {
                return Err(KrakenError::ParseError(
                    format!("Kraken API error: {:?}", errors)
                ));
            }
        }

        let result = json.get("result")
            .ok_or_else(|| KrakenError::MissingField("result".to_string()))?;

        let count = result.get("count")
            .and_then(|c| c.as_u64())
            .ok_or_else(|| KrakenError::ParseError("Missing count field".to_string()))?;

        Ok(count > 0)
    }

    pub fn get_balance(&self) -> Result<HashMap<String, f64>, KrakenError> {
        let nonce = self.generate_nonce();
        let body = format!("nonce={}", nonce);

        let path = "/0/private/Balance";
        let url = format!("https://api.kraken.com{}", path);

        let message = self.create_signature_message(path, &nonce, &body);
        let signature = self.sign_message(&message)?;

        let response = self.client
            .post(&url)
            .header("API-Key", &self.api_key)
            .header("API-Sign", signature)
            .header("Content-Type", "application/x-www-form-urlencoded")
            .body(body)
            .send()
            .map_err(KrakenError::HttpError)?;

        let json: serde_json::Value = response.json()
            .map_err(|e| KrakenError::ParseError(e.to_string()))?;

        if let Some(errors) = json.get("error").and_then(serde_json::Value::as_array) {
            if !errors.is_empty() {
                return Err(KrakenError::ParseError(
                    format!("Kraken API error: {:?}", errors)
                ));
            }
        }

        let result = json.get("result")
            .ok_or_else(|| KrakenError::MissingField("result".to_string()))?;

        let balances = result.as_object()
            .ok_or_else(|| KrakenError::ParseError("Expected result to be an object".to_string()))?
            .iter()
            .filter_map(|(k, v)| {
                v.as_str()
                    .and_then(|s| s.parse::<f64>().ok())
                    .map(|val| (k.clone(), val))
            })
            .collect();

        Ok(balances)
    }

    pub fn add_order(&self, pair: &str, side: &str, price: f64, volume: f64) -> Result<OrderResponse, KrakenError> {
        let side_lower = side.to_lowercase();
        if side_lower != "buy" && side_lower != "sell" {
            return Err(KrakenError::ParseError(
                "Side must be 'buy' or 'sell'".to_string()
            ));
        }

        let nonce = self.generate_nonce();
        
        let params = vec![
            ("nonce".to_string(), nonce.clone()),
            ("ordertype".to_string(), "limit".to_string()),
            ("type".to_string(), side_lower),
            ("volume".to_string(), volume.to_string()),
            ("price".to_string(), price.to_string()),
            ("pair".to_string(), pair.to_string()),
        ];

        let body = params
            .iter()
            .map(|(k, v)| format!("{}={}", k, v))
            .collect::<Vec<String>>()
            .join("&");

        let path = "/0/private/AddOrder";
        let url = format!("https://api.kraken.com{}", path);

        let message = self.create_signature_message(path, &nonce, &body);
        let signature = self.sign_message(&message)?;

        let response = self.client
            .post(&url)
            .header("API-Key", &self.api_key)
            .header("API-Sign", signature)
            .header("Content-Type", "application/x-www-form-urlencoded")
            .body(body)
            .send()
            .map_err(KrakenError::HttpError)?;

        let json: serde_json::Value = response.json()
            .map_err(|e| KrakenError::ParseError(e.to_string()))?;

        if let Some(errors) = json.get("error").and_then(serde_json::Value::as_array) {
            if !errors.is_empty() {
                return Err(KrakenError::ParseError(
                    format!("Kraken API error: {:?}", errors)
                ));
            }
        }

        let result = json.get("result")
            .ok_or_else(|| KrakenError::MissingField("result".to_string()))?;

        let txid = result.get("txid")
            .and_then(|t| t.as_array())
            .ok_or_else(|| KrakenError::ParseError("Missing txid array".to_string()))?
            .iter()
            .filter_map(|v| v.as_str().map(|s| s.to_string()))
            .collect::<Vec<String>>();

        let description = result.get("descr")
            .and_then(|d| d.get("order"))
            .and_then(|o| o.as_str())
            .unwrap_or("No description available")
            .to_string();

        Ok(OrderResponse {
            txid,
            description,
        })
    }
}
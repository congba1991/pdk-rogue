use pyo3::prelude::*;
use pyo3::types::PyString;
use serde::Deserialize;
use rand::seq::SliceRandom;

#[derive(Deserialize, Clone)]
pub struct Card {
    pub rank: String,
    pub suit: String,
}

use std::collections::HashMap;

#[derive(Clone, Debug, PartialEq, Eq, Hash, serde::Deserialize)]
pub struct Card {
    pub rank: String,
    pub suit: String,
}

#[derive(Clone, Debug)]
pub struct Combo {
    pub cards: Vec<Card>,
    pub combo_type: String, // "SINGLE", "PAIR", "TRIPLE"
    pub lead_value: u8,
}

fn card_value(rank: &str) -> u8 {
    match rank {
        "3" => 3, "4" => 4, "5" => 5, "6" => 6, "7" => 7, "8" => 8, "9" => 9, "10" => 10,
        "J" => 11, "Q" => 12, "K" => 13, "A" => 14, "2" => 15,
        _ => 0,
    }
}

pub fn find_opponent_valid_plays(hand: &[Card], last_combo: Option<&Combo>) -> Vec<Combo> {
    let mut value_groups: HashMap<u8, Vec<Card>> = HashMap::new();
    for card in hand {
        value_groups.entry(card_value(&card.rank)).or_default().push(card.clone());
    }
    let mut valid_combos = Vec::new();

    if last_combo.is_none() {
        // Singles
        for card in hand {
            valid_combos.push(Combo {
                cards: vec![card.clone()],
                combo_type: "SINGLE".to_string(),
                lead_value: card_value(&card.rank),
            });
        }
        // Pairs
        for cards in value_groups.values() {
            if cards.len() >= 2 {
                valid_combos.push(Combo {
                    cards: cards[0..2].to_vec(),
                    combo_type: "PAIR".to_string(),
                    lead_value: card_value(&cards[0].rank),
                });
            }
        }
        // Triples
        for cards in value_groups.values() {
            if cards.len() >= 3 {
                valid_combos.push(Combo {
                    cards: cards[0..3].to_vec(),
                    combo_type: "TRIPLE".to_string(),
                    lead_value: card_value(&cards[0].rank),
                });
            }
        }
    } else {
        let last = last_combo.unwrap();
        match last.combo_type.as_str() {
            "SINGLE" => {
                for card in hand {
                    if card_value(&card.rank) > last.lead_value {
                        valid_combos.push(Combo {
                            cards: vec![card.clone()],
                            combo_type: "SINGLE".to_string(),
                            lead_value: card_value(&card.rank),
                        });
                    }
                }
            }
            "PAIR" => {
                for cards in value_groups.values() {
                    if cards.len() >= 2 && card_value(&cards[0].rank) > last.lead_value {
                        valid_combos.push(Combo {
                            cards: cards[0..2].to_vec(),
                            combo_type: "PAIR".to_string(),
                            lead_value: card_value(&cards[0].rank),
                        });
                    }
                }
            }
            "TRIPLE" => {
                for cards in value_groups.values() {
                    if cards.len() >= 3 && card_value(&cards[0].rank) > last.lead_value {
                        valid_combos.push(Combo {
                            cards: cards[0..3].to_vec(),
                            combo_type: "TRIPLE".to_string(),
                            lead_value: card_value(&cards[0].rank),
                        });
                    }
                }
            }
            _ => {}
        }
    }
    valid_combos
}

#[pyfunction]
fn simulate_playout_py(
    ai_hand_json: &PyString,
    player_hand_json: &PyString,
    play_json: &PyString,
    last_combo_json: &PyString,
    is_ai_turn: bool
) -> PyResult<bool> {
    let mut ai_hand: Vec<Card> = serde_json::from_str(ai_hand_json.to_str()?).unwrap();
    let mut player_hand: Vec<Card> = serde_json::from_str(player_hand_json.to_str()?).unwrap();
    let play: Vec<Card> = serde_json::from_str(play_json.to_str()?).unwrap();
    // Parse last_combo if present
    let last_combo: Option<Combo> = match serde_json::from_str::<Combo>(last_combo_json.to_str()?) {
        Ok(combo) => Some(combo),
        Err(_) => None,
    };

    // Remove played cards from AI hand
    ai_hand.retain(|c| !play.iter().any(|p| p.rank == c.rank && p.suit == c.suit));
    let mut ai_hp = 10;
    let mut player_hp = 10;
    let mut ai_turn = !is_ai_turn;
    let mut last_combo = if !play.is_empty() {
        Some(Combo {
            cards: play.clone(),
            combo_type: if play.len() == 1 {
                "SINGLE".to_string()
            } else if play.len() == 2 {
                "PAIR".to_string()
            } else if play.len() == 3 {
                "TRIPLE".to_string()
            } else {
                "SINGLE".to_string() // fallback
            },
            lead_value: play.iter().map(|c| card_value(&c.rank)).max().unwrap_or(0),
        })
    } else {
        None
    };

    use rand::seq::SliceRandom;
    let mut rng = rand::thread_rng();

    while !ai_hand.is_empty() && !player_hand.is_empty() && ai_hp > 0 && player_hp > 0 {
        if ai_turn {
            // AI's turn: play random valid move or pass
            let valid = find_opponent_valid_plays(&ai_hand, last_combo.as_ref());
            if !valid.is_empty() {
                let mv = valid.choose(&mut rng).unwrap();
                for c in &mv.cards {
                    if let Some(pos) = ai_hand.iter().position(|x| x.rank == c.rank && x.suit == c.suit) {
                        ai_hand.remove(pos);
                    }
                }
                last_combo = Some(mv.clone());
            } else {
                last_combo = None;
                ai_hp -= 1;
            }
        } else {
            // Opponent's turn: play random valid move or pass
            let valid = find_opponent_valid_plays(&player_hand, last_combo.as_ref());
            if !valid.is_empty() {
                let mv = valid.choose(&mut rng).unwrap();
                for c in &mv.cards {
                    if let Some(pos) = player_hand.iter().position(|x| x.rank == c.rank && x.suit == c.suit) {
                        player_hand.remove(pos);
                    }
                }
                last_combo = Some(mv.clone());
            } else {
                last_combo = None;
                player_hp -= 1;
            }
        }
        ai_turn = !ai_turn;
    }
    Ok(ai_hand.is_empty() || player_hp <= 0)
}

#[pymodule]
fn mcts_rust(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(simulate_playout_py, m)?)?;
    Ok(())
}
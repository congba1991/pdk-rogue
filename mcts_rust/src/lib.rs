// Simple evaluation: +1 for AI win, -1 for player win, 0 otherwise
fn evaluate(ai_hand: &[Card], player_hand: &[Card], ai_hp: i32, player_hp: i32) -> i32 {
    if ai_hand.is_empty() || player_hp <= 0 {
        1
    } else if player_hand.is_empty() || ai_hp <= 0 {
        -1
    } else {
        0
    }
}

fn alpha_beta(
    ai_hand: &mut Vec<Card>,
    player_hand: &mut Vec<Card>,
    ai_hp: i32,
    player_hp: i32,
    ai_turn: bool,
    last_combo: Option<Combo>,
    depth: usize,
    alpha: i32,
    beta: i32,
) -> i32 {
    // Terminal state or depth limit
    if ai_hand.is_empty() || player_hand.is_empty() || ai_hp <= 0 || player_hp <= 0 || depth == 0 {
        return evaluate(ai_hand, player_hand, ai_hp, player_hp);
    }
    let mut alpha = alpha;
    let mut beta = beta;
    if ai_turn {
        // Maximizing player (AI)
        let valid = find_opponent_valid_plays(ai_hand, last_combo.as_ref());
        if valid.is_empty() {
            // Pass: lose 1 HP
            let score = alpha_beta(
                ai_hand,
                player_hand,
                ai_hp - 1,
                player_hp,
                false,
                None,
                depth - 1,
                alpha,
                beta,
            );
            alpha = alpha.max(score);
            return alpha;
        }
        let mut value = i32::MIN;
        for mv in valid {
            // Remove played cards
            let mut new_ai = ai_hand.clone();
            for c in &mv.cards {
                if let Some(pos) = new_ai.iter().position(|x| x.rank == c.rank && x.suit == c.suit) {
                    new_ai.remove(pos);
                }
            }
            let score = alpha_beta(
                &mut new_ai,
                player_hand,
                ai_hp,
                player_hp,
                false,
                Some(mv.clone()),
                depth - 1,
                alpha,
                beta,
            );
            value = value.max(score);
            alpha = alpha.max(value);
            if alpha >= beta {
                break;
            }
        }
        value
    } else {
        // Minimizing player (opponent)
        let valid = find_opponent_valid_plays(player_hand, last_combo.as_ref());
        if valid.is_empty() {
            // Pass: lose 1 HP
            let score = alpha_beta(
                ai_hand,
                player_hand,
                ai_hp,
                player_hp - 1,
                true,
                None,
                depth - 1,
                alpha,
                beta,
            );
            beta = beta.min(score);
            return beta;
        }
        let mut value = i32::MAX;
        for mv in valid {
            let mut new_player = player_hand.clone();
            for c in &mv.cards {
                if let Some(pos) = new_player.iter().position(|x| x.rank == c.rank && x.suit == c.suit) {
                    new_player.remove(pos);
                }
            }
            let score = alpha_beta(
                ai_hand,
                &mut new_player,
                ai_hp,
                player_hp,
                true,
                Some(mv.clone()),
                depth - 1,
                alpha,
                beta,
            );
            value = value.min(score);
            beta = beta.min(value);
            if alpha >= beta {
                break;
            }
        }
        value
    }
}

#[pyfunction]
fn alpha_beta_py(
    ai_hand_json: &PyString,
    player_hand_json: &PyString,
    play_json: &PyString,
    last_combo_json: &PyString,
    is_ai_turn: bool,
    depth: usize
) -> PyResult<i32> {
    let mut ai_hand: Vec<Card> = serde_json::from_str(ai_hand_json.to_str()?).unwrap();
    let mut player_hand: Vec<Card> = serde_json::from_str(player_hand_json.to_str()?).unwrap();
    let play: Vec<Card> = serde_json::from_str(play_json.to_str()?).unwrap();
    let last_combo: Option<Combo> = match serde_json::from_str::<Combo>(last_combo_json.to_str()?) {
        Ok(combo) => Some(combo),
        Err(_) => None,
    };
    // Remove played cards from AI hand
    ai_hand.retain(|c| !play.iter().any(|p| p.rank == c.rank && p.suit == c.suit));
    let ai_hp = 10;
    let player_hp = 10;
    let ai_turn = !is_ai_turn;
    let last_combo = if !play.is_empty() {
        // Try to detect the combo type based on the cards in play
        let combo_type = if play.len() == 1 {
            "SINGLE".to_string()
        } else if play.len() == 2 && play[0].rank == play[1].rank {
            "PAIR".to_string()
        } else if play.len() == 3 && play.iter().all(|c| c.rank == play[0].rank) {
            "TRIPLE".to_string()
        } else if play.len() == 4 && play.iter().all(|c| c.rank == play[0].rank) {
            "BOMB".to_string()
        } else {
            // Check for straight
            let mut values: Vec<u8> = play.iter().map(|c| card_value(&c.rank)).collect();
            values.sort_unstable();
            values.dedup();
            let is_straight = values.len() == play.len()
                && values.windows(2).all(|w| w[1] == w[0] + 1)
                && *values.last().unwrap_or(&0) <= 14;
            if is_straight && play.len() >= 5 {
                "STRAIGHT".to_string()
            } else {
                // Check for plane (multiple consecutive triples)
                let mut value_counts = std::collections::HashMap::new();
                for c in &play {
                    *value_counts.entry(&c.rank).or_insert(0) += 1;
                }
                let triple_ranks: Vec<_> = value_counts.iter().filter(|(_, v)| **v == 3).map(|(r, _)| r.as_str()).collect();
                let mut triple_values: Vec<u8> = triple_ranks.iter().map(|r| card_value(r)).collect();
                triple_values.sort_unstable();
                let is_plane = triple_values.len() >= 2
                    && triple_values.windows(2).all(|w| w[1] == w[0] + 1)
                    && triple_values.iter().all(|&v| v < 15);
                if is_plane && play.len() == triple_values.len() * 3 {
                    "PLANE".to_string()
                } else {
                    "SINGLE".to_string() // fallback
                }
            }
        };
        Some(Combo {
            cards: play.clone(),
            combo_type,
            lead_value: play.iter().map(|c| card_value(&c.rank)).max().unwrap_or(0),
        })
    } else {
        None
    };
    let result = alpha_beta(
        &mut ai_hand,
        &mut player_hand,
        ai_hp,
        player_hp,
        ai_turn,
        last_combo,
        depth,
        i32::MIN + 1,
        i32::MAX - 1,
    );
    Ok(result)
}
use pyo3::prelude::*;
use pyo3::types::PyString;
use rand::seq::SliceRandom;
use rayon::prelude::*;

use std::collections::HashMap;

#[derive(Clone, Debug, PartialEq, Eq, Hash, serde::Deserialize)]
pub struct Card {
    pub rank: String,
    pub suit: String,
}

#[derive(Clone, Debug, serde::Deserialize)]
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

    // Helper for straight detection
    fn find_straights(hand: &[Card], target_length: Option<usize>) -> Vec<Combo> {
        let mut straights = Vec::new();
        let mut values: Vec<u8> = hand.iter().map(|c| card_value(&c.rank)).filter(|&v| v <= 14).collect();
        values.sort_unstable();
        values.dedup();
        let min_length = target_length.unwrap_or(5);
        for start in 0..values.len() {
            for end in (start + min_length - 1)..values.len() {
                let mut is_consecutive = true;
                for i in (start + 1)..=end {
                    if values[i] != values[i - 1] + 1 {
                        is_consecutive = false;
                        break;
                    }
                }
                if is_consecutive {
                    let length = end - start + 1;
                    if target_length.is_none() || length == target_length.unwrap() {
                        let mut straight_cards = Vec::new();
                        for v in &values[start..=end] {
                            for c in hand {
                                if card_value(&c.rank) == *v && !straight_cards.contains(c) {
                                    straight_cards.push(c.clone());
                                    break;
                                }
                            }
                        }
                        if straight_cards.len() == length {
                            straights.push(Combo {
                                cards: straight_cards,
                                combo_type: "STRAIGHT".to_string(),
                                lead_value: *values[start..=end].iter().max().unwrap(),
                            });
                        }
                    }
                }
            }
        }
        straights
    }

    // Helper for plane detection (no wings)
    fn find_planes(hand: &[Card]) -> Vec<Combo> {
        let mut planes = Vec::new();
        let mut value_groups: HashMap<u8, Vec<Card>> = HashMap::new();
        for card in hand {
            value_groups.entry(card_value(&card.rank)).or_default().push(card.clone());
        }
        let mut triple_values: Vec<u8> = value_groups.iter().filter(|(_, v)| v.len() >= 3 && v[0].rank != "2").map(|(k, _)| *k).collect();
        triple_values.sort_unstable();
        for start in 0..triple_values.len() {
            let mut consecutive = vec![triple_values[start]];
            for i in (start + 1)..triple_values.len() {
                if triple_values[i] == consecutive.last().unwrap() + 1 {
                    consecutive.push(triple_values[i]);
                } else {
                    break;
                }
            }
            if consecutive.len() >= 2 {
                for length in 2..=consecutive.len() {
                    let mut plane_base = Vec::new();
                    for v in &consecutive[..length] {
                        for c in &value_groups[v] {
                            if plane_base.len() < length * 3 {
                                plane_base.push(c.clone());
                            }
                        }
                    }
                    if plane_base.len() == length * 3 {
                        planes.push(Combo {
                            cards: plane_base.clone(),
                            combo_type: "PLANE".to_string(),
                            lead_value: *consecutive[..length].iter().max().unwrap(),
                        });
                    }
                }
            }
        }
        planes
    }

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
        // Straights
        valid_combos.extend(find_straights(hand, None));
        // Planes
        valid_combos.extend(find_planes(hand));
        // Bombs (4 of a kind)
        for cards in value_groups.values() {
            if cards.len() == 4 {
                valid_combos.push(Combo {
                    cards: cards.clone(),
                    combo_type: "BOMB".to_string(),
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
            "STRAIGHT" => {
                let straights = find_straights(hand, Some(last.cards.len()));
                for combo in straights {
                    if combo.lead_value > last.lead_value {
                        valid_combos.push(combo);
                    }
                }
            }
            "PLANE" => {
                let planes = find_planes(hand);
                for combo in planes {
                    if combo.lead_value > last.lead_value {
                        valid_combos.push(combo);
                    }
                }
            }
            _ => {}
        }
        // Bombs always allowed if not already a bomb
        if last.combo_type.as_str() != "BOMB" {
            for cards in value_groups.values() {
                if cards.len() == 4 {
                    valid_combos.push(Combo {
                        cards: cards.clone(),
                        combo_type: "BOMB".to_string(),
                        lead_value: card_value(&cards[0].rank),
                    });
                }
            }
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
    is_ai_turn: bool,
    use_alpha_beta: bool,
    depth: usize
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
        // Try to detect the combo type based on the cards in play
        let combo_type = if play.len() == 1 {
            "SINGLE".to_string()
        } else if play.len() == 2 && play[0].rank == play[1].rank {
            "PAIR".to_string()
        } else if play.len() == 3 && play.iter().all(|c| c.rank == play[0].rank) {
            "TRIPLE".to_string()
        } else if play.len() == 4 && play.iter().all(|c| c.rank == play[0].rank) {
            "BOMB".to_string()
        } else {
            // Check for straight
            let mut values: Vec<u8> = play.iter().map(|c| card_value(&c.rank)).collect();
            values.sort_unstable();
            values.dedup();
            let is_straight = values.len() == play.len()
                && values.windows(2).all(|w| w[1] == w[0] + 1)
                && *values.last().unwrap_or(&0) <= 14;
            if is_straight && play.len() >= 5 {
                "STRAIGHT".to_string()
            } else {
                // Check for plane (multiple consecutive triples)
                let mut value_counts = std::collections::HashMap::new();
                for c in &play {
                    *value_counts.entry(&c.rank).or_insert(0) += 1;
                }
                let triple_ranks: Vec<_> = value_counts.iter().filter(|(_, v)| **v == 3).map(|(r, _)| r.as_str()).collect();
                let mut triple_values: Vec<u8> = triple_ranks.iter().map(|r| card_value(r)).collect();
                triple_values.sort_unstable();
                let is_plane = triple_values.len() >= 2
                    && triple_values.windows(2).all(|w| w[1] == w[0] + 1)
                    && triple_values.iter().all(|&v| v < 15);
                if is_plane && play.len() == triple_values.len() * 3 {
                    "PLANE".to_string()
                } else {
                    "SINGLE".to_string() // fallback
                }
            }
        };
        Some(Combo {
            cards: play.clone(),
            combo_type,
            lead_value: play.iter().map(|c| card_value(&c.rank)).max().unwrap_or(0),
        })
    } else {
        None
    };

    use rand::seq::SliceRandom;
    let mut rng = rand::thread_rng();

    if use_alpha_beta {
        // Use alpha-beta to evaluate the outcome from this state
        let result = alpha_beta(
            &mut ai_hand,
            &mut player_hand,
            ai_hp,
            player_hp,
            ai_turn,
            last_combo,
            depth,
            i32::MIN + 1,
            i32::MAX - 1,
        );
        Ok(result == 1)
    } else {
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
}

#[pymodule]
fn mcts_rust(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(simulate_playout_py, m)?)?;
    m.add_function(wrap_pyfunction!(simulate_playouts_parallel_py, m)?)?;
    m.add_function(wrap_pyfunction!(alpha_beta_py, m)?)?;
    Ok(())
}

#[pyfunction]
fn simulate_playouts_parallel_py(
    ai_hand_json: &PyString,
    player_hand_json: &PyString,
    play_json: &PyString,
    last_combo_json: &PyString,
    is_ai_turn: bool,
    num_simulations: usize,
    use_alpha_beta: bool,
    depth: usize
) -> PyResult<usize> {
    let ai_hand_str = ai_hand_json.to_str()?;
    let player_hand_str = player_hand_json.to_str()?;
    let play_str = play_json.to_str()?;
    let last_combo_str = last_combo_json.to_str()?;
    let wins = (0..num_simulations).into_par_iter().map(|_| {
        let mut ai_hand: Vec<Card> = serde_json::from_str(ai_hand_str).unwrap();
        let mut player_hand: Vec<Card> = serde_json::from_str(player_hand_str).unwrap();
        let play: Vec<Card> = serde_json::from_str(play_str).unwrap();
        let last_combo: Option<Combo> = match serde_json::from_str::<Combo>(last_combo_str) {
            Ok(combo) => Some(combo),
            Err(_) => None,
        };
        // Remove played cards from AI hand
        ai_hand.retain(|c| !play.iter().any(|p| p.rank == c.rank && p.suit == c.suit));
        let mut ai_hp = 10;
        let mut player_hp = 10;
        let mut ai_turn = !is_ai_turn;
        let mut last_combo = if !play.is_empty() {
            // Try to detect the combo type based on the cards in play
            let combo_type = if play.len() == 1 {
                "SINGLE".to_string()
            } else if play.len() == 2 && play[0].rank == play[1].rank {
                "PAIR".to_string()
            } else if play.len() == 3 && play.iter().all(|c| c.rank == play[0].rank) {
                "TRIPLE".to_string()
            } else if play.len() == 4 && play.iter().all(|c| c.rank == play[0].rank) {
                "BOMB".to_string()
            } else {
                // Check for straight
                let mut values: Vec<u8> = play.iter().map(|c| card_value(&c.rank)).collect();
                values.sort_unstable();
                values.dedup();
                let is_straight = values.len() == play.len()
                    && values.windows(2).all(|w| w[1] == w[0] + 1)
                    && *values.last().unwrap_or(&0) <= 14;
                if is_straight && play.len() >= 5 {
                    "STRAIGHT".to_string()
                } else {
                    // Check for plane (multiple consecutive triples)
                    let mut value_counts = std::collections::HashMap::new();
                    for c in &play {
                        *value_counts.entry(&c.rank).or_insert(0) += 1;
                    }
                    let triple_ranks: Vec<_> = value_counts.iter().filter(|(_, v)| **v == 3).map(|(r, _)| r.as_str()).collect();
                    let mut triple_values: Vec<u8> = triple_ranks.iter().map(|r| card_value(r)).collect();
                    triple_values.sort_unstable();
                    let is_plane = triple_values.len() >= 2
                        && triple_values.windows(2).all(|w| w[1] == w[0] + 1)
                        && triple_values.iter().all(|&v| v < 15);
                    if is_plane && play.len() == triple_values.len() * 3 {
                        "PLANE".to_string()
                    } else {
                        "SINGLE".to_string() // fallback
                    }
                }
            };
            Some(Combo {
                cards: play.clone(),
                combo_type,
                lead_value: play.iter().map(|c| card_value(&c.rank)).max().unwrap_or(0),
            })
        } else {
            None
        };
        if use_alpha_beta {
            let result = alpha_beta(
                &mut ai_hand,
                &mut player_hand,
                ai_hp,
                player_hp,
                ai_turn,
                last_combo,
                depth,
                i32::MIN + 1,
                i32::MAX - 1,
            );
            result == 1
        } else {
            let mut rng = rand::thread_rng();
            while !ai_hand.is_empty() && !player_hand.is_empty() && ai_hp > 0 && player_hp > 0 {
                if ai_turn {
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
            ai_hand.is_empty() || player_hp <= 0
        }
    }).filter(|&win| win).count();
    Ok(wins)
}
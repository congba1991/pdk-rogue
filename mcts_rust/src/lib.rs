// Evaluate overall hand strength (like _evaluate_hand_strength)
fn evaluate_hand_strength(hand: &[Card]) -> i32 {
    if hand.is_empty() {
        return 0;
    }
    let mut strength = 0;
    for card in hand {
        let v = card_value(&card.rank);
        if v >= 13 { // K, A, 2
            strength += (v as i32 - 10) * 3;
        }
    }
    let mut value_counts = std::collections::HashMap::new();
    for card in hand {
        *value_counts.entry(&card.rank).or_insert(0) += 1;
    }
    for v in value_counts.values() {
        if *v == 4 {
            strength += 50;
        }
    }
    strength
}

// Count control cards (like _count_controls)
fn count_controls(hand: &[Card]) -> f32 {
    let mut value_counts = std::collections::HashMap::new();
    for card in hand {
        *value_counts.entry(&card.rank).or_insert(0) += 1;
    }
    let mut controls = 0.0;
    controls += *value_counts.get(&"2".to_string()).unwrap_or(&0) as f32;
    controls += *value_counts.get(&"A".to_string()).unwrap_or(&0) as f32 * 0.7;
    for v in value_counts.values() {
        if *v == 4 {
            controls += 2.0;
        }
    }
    controls
}

// Analyze hand shape (like _analyze_hand_shape)
fn analyze_hand_shape(hand: &[Card]) -> i32 {
    if hand.is_empty() {
        return 0;
    }
    let mut value_counts = std::collections::HashMap::new();
    for card in hand {
        *value_counts.entry(&card.rank).or_insert(0) += 1;
    }
    let mut shape_score = 0;
    let singles = value_counts.values().filter(|&&v| v == 1).count() as i32;
    shape_score -= singles * 5;
    let pairs = value_counts.values().filter(|&&v| v == 2).count() as i32;
    let triples = value_counts.values().filter(|&&v| v == 3).count() as i32;
    shape_score += pairs * 3 + triples * 5;
    let mut values: Vec<u8> = value_counts.keys().map(|r| card_value(r)).collect();
    values.sort_unstable();
    let mut consecutive = 0;
    for i in 1..values.len() {
        if values[i] == values[i-1] + 1 && values[i] <= 14 {
            consecutive += 1;
        } else {
            if consecutive >= 4 {
                shape_score += consecutive * 2;
            }
            consecutive = 0;
        }
    }
    shape_score
}

// Estimate minimum turns to win (like _estimate_turns_to_win)
fn estimate_turns_to_win(hand: &[Card]) -> i32 {
    if hand.is_empty() {
        return 0;
    }
    let mut value_groups: std::collections::HashMap<&String, Vec<&Card>> = std::collections::HashMap::new();
    for card in hand {
        value_groups.entry(&card.rank).or_default().push(card);
    }
    let mut turns = 0;
    let mut remaining_cards: Vec<&Card> = hand.iter().collect();
    // Bombs
    for (value, cards) in value_groups.iter() {
        if cards.len() == 4 {
            turns += 1;
            remaining_cards.retain(|c| &c.rank != *value);
        }
    }
    // Triples
    let mut value_groups: std::collections::HashMap<&String, Vec<&Card>> = std::collections::HashMap::new();
    for card in &remaining_cards {
        value_groups.entry(&card.rank).or_default().push(card);
    }
    for (value, cards) in value_groups.clone() {
        if cards.len() >= 3 {
            turns += 1;
            let mut count = 0;
            remaining_cards.retain(|c| {
                if &c.rank == value && count < 3 {
                    count += 1;
                    false
                } else {
                    true
                }
            });
        }
    }
    // Pairs
    let mut value_groups: std::collections::HashMap<&String, Vec<&Card>> = std::collections::HashMap::new();
    for card in &remaining_cards {
        value_groups.entry(&card.rank).or_default().push(card);
    }
    for (value, cards) in value_groups.clone() {
        if cards.len() >= 2 {
            turns += 1;
            let mut found = 0;
            remaining_cards.retain(|c| {
                if &c.rank == value && found < 2 {
                    found += 1;
                    false
                } else {
                    true
                }
            });
        }
    }
    // Singles
    turns += remaining_cards.len() as i32;
    std::cmp::max(turns, (hand.len() as i32) / 5)
}

// Evaluate the current game position with a specific hand (like _evaluate_position_with_hand)
fn evaluate_position_with_hand(hand: &[Card]) -> i32 {
    let mut score = 0;
    let hand_strength = evaluate_hand_strength(hand);
    score += hand_strength * 10;
    score -= hand.len() as i32 * 50;
    let controls = count_controls(hand);
    score += (controls * 100.0) as i32;
    let shape_score = analyze_hand_shape(hand);
    score += shape_score * 20;
    let turns = estimate_turns_to_win(hand);
    score -= turns * 200;
    score
}
// Estimate likely opponent responses for a given last_combo
fn estimate_opponent_responses(player_hand: &[Card], last_combo: Option<&Combo>) -> Vec<Combo> {
    let mut responses = Vec::new();
    let valid_plays = find_opponent_valid_plays(player_hand, last_combo);
    if last_combo.is_none() {
        // If no last combo, return a few low and mid-value singles/pairs, and pass
        let mut singles: Vec<_> = valid_plays.iter().filter(|c| c.combo_type == "SINGLE").collect();
        singles.sort_by_key(|c| c.lead_value);
        for s in singles.iter().take(2) {
            responses.push((*s).clone());
        }
        let mut pairs: Vec<_> = valid_plays.iter().filter(|c| c.combo_type == "PAIR").collect();
        pairs.sort_by_key(|c| c.lead_value);
        if let Some(p) = pairs.get(0) { responses.push((*p).clone()); }
        responses.push(Combo { cards: vec![], combo_type: "PASS".to_string(), lead_value: 0 });
    } else {
        // Try to beat last_combo with valid plays
        for c in valid_plays.iter() {
            if c.lead_value > last_combo.unwrap().lead_value {
                responses.push(c.clone());
            }
        }
        responses.push(Combo { cards: vec![], combo_type: "PASS".to_string(), lead_value: 0 });
        // Consider bomb if not already a bomb
        if last_combo.unwrap().combo_type != "BOMB" {
            let bombs: Vec<_> = valid_plays.iter().filter(|c| c.combo_type == "BOMB").collect();
            if let Some(b) = bombs.get(0) { responses.push((*b).clone()); }
        }
    }
    // Limit to 5 for performance
    responses.truncate(5);
    responses
}

// Evaluate a specific move with a specific hand (Rust version of _evaluate_move_with_hand)
fn evaluate_move_with_hand(combo: &Combo, last_combo: Option<&Combo>, hand: &[Card]) -> i32 {
    if combo.combo_type == "PASS" {
        return -50;
    }
    let mut score = 0;
    // Prefer to get rid of low singles early
    if combo.combo_type == "SINGLE" && combo.lead_value < 10 {
        score += 30;
    }
    // Prefer to keep high cards and bombs
    let avg_value = if !combo.cards.is_empty() {
        combo.cards.iter().map(|c| card_value(&c.rank) as i32).sum::<i32>() / combo.cards.len() as i32
    } else { 0 };
    score -= avg_value * 2;
    // Bonus for using many cards at once
    score += combo.cards.len() as i32 * 10;
    // Penalty for breaking up potential combinations (simple: count pairs/triples before/after)
    let mut value_counts = std::collections::HashMap::new();
    for c in hand {
        *value_counts.entry(&c.rank).or_insert(0) += 1;
    }
    let shape_before = value_counts.values().filter(|&&v| v == 2).count() as i32 * 3 + value_counts.values().filter(|&&v| v == 3).count() as i32 * 5;
    let mut remaining_hand = hand.to_vec();
    for c in &combo.cards {
        if let Some(pos) = remaining_hand.iter().position(|x| x.rank == c.rank && x.suit == c.suit) {
            remaining_hand.remove(pos);
        }
    }
    let mut value_counts_after = std::collections::HashMap::new();
    for c in &remaining_hand {
        *value_counts_after.entry(&c.rank).or_insert(0) += 1;
    }
    let shape_after = value_counts_after.values().filter(|&&v| v == 2).count() as i32 * 3 + value_counts_after.values().filter(|&&v| v == 3).count() as i32 * 5;
    score -= (shape_before - shape_after) * 15;
    // Penalty for using bombs too early
    if combo.combo_type == "BOMB" && hand.len() > 10 {
        score -= 200;
    }
    score
}
use serde::{Serialize, Deserialize};

#[pyfunction]
fn minimax_search_py(
    ai_hand_json: &PyString,
    last_combo_json: &PyString,
    player_hand_json: &PyString,
    ai_hp: i32,
    player_hp: i32,
    depth: usize
) -> PyResult<String> {
    let ai_hand: Vec<Card> = serde_json::from_str(ai_hand_json.to_str()?).unwrap();
    let player_hand: Vec<Card> = serde_json::from_str(player_hand_json.to_str()?).unwrap();
    let last_combo: Option<Combo> = match serde_json::from_str::<Combo>(last_combo_json.to_str()?) {
        Ok(combo) => Some(combo),
        Err(_) => None,
    };
    let (best_combo, _score) = minimax_search(
        &ai_hand,
        &player_hand,
        ai_hp,
        player_hp,
        last_combo.as_ref(),
        depth,
        true,
        i32::MIN + 1,
        i32::MAX - 1,
    );
    let result = match best_combo {
        Some(combo) => serde_json::to_string(&combo).unwrap(),
        None => "null".to_string(),
    };
    Ok(result)
}

fn minimax_search(
    ai_hand: &[Card],
    player_hand: &[Card],
    ai_hp: i32,
    player_hp: i32,
    last_combo: Option<&Combo>,
    depth: usize,
    is_maximizing: bool,
    mut alpha: i32,
    mut beta: i32,
) -> (Option<Combo>, i32) {
    // Terminal or depth limit
    if depth == 0 || ai_hand.is_empty() || player_hand.is_empty() || ai_hp <= 0 || player_hp <= 0 {
        let eval = evaluate_position_with_hand(ai_hand) - evaluate_position_with_hand(player_hand);
        return (None, eval);
    }
    if is_maximizing {
        let mut valid_plays = find_opponent_valid_plays(ai_hand, last_combo);
        if last_combo.is_some() {
            valid_plays.push(Combo { cards: vec![], combo_type: "PASS".to_string(), lead_value: 0 });
        }
        let results: Vec<(Combo, i32)> = valid_plays.par_iter().map(|play| {
            let mut new_ai = ai_hand.to_vec();
            let mut new_ai_hp = ai_hp;
            let mut new_last_combo = last_combo.cloned();
            if play.combo_type == "PASS" {
                new_ai_hp -= 1;
                new_last_combo = last_combo.cloned();
            } else {
                for c in &play.cards {
                    if let Some(pos) = new_ai.iter().position(|x| x.rank == c.rank && x.suit == c.suit) {
                        new_ai.remove(pos);
                    }
                }
                new_last_combo = Some(play.clone());
            }
            // Generate opponent's possible responses
            let opponent_plays = estimate_opponent_responses(player_hand, new_last_combo.as_ref());
            // Recursively evaluate with the new hand state
            let mut eval = i32::MIN;
            for opp_play in &opponent_plays {
                let (_opp_play, opp_eval) = minimax_search(
                    &new_ai,
                    player_hand,
                    new_ai_hp,
                    player_hp,
                    Some(opp_play),
                    depth - 1,
                    false,
                    alpha,
                    beta,
                );
                eval = eval.max(opp_eval);
            }
            // Add immediate move evaluation
            if play.combo_type != "PASS" {
                eval += (evaluate_move_with_hand(play, last_combo, ai_hand) as f32 * 0.3) as i32;
            }
            (play.clone(), eval)
        }).collect();
        // Find the best result
        let (best_play, max_eval) = results.into_iter().max_by_key(|(_, eval)| *eval).map(|(p, e)| (Some(p), e)).unwrap_or((None, i32::MIN));
        (best_play, max_eval)
    } else {
        let mut min_eval = i32::MAX;
        let mut best_play = None;
        let mut valid_plays = find_opponent_valid_plays(player_hand, last_combo);
        if last_combo.is_some() {
            valid_plays.push(Combo { cards: vec![], combo_type: "PASS".to_string(), lead_value: 0 });
        }
        for play in valid_plays {
            let mut new_player = player_hand.to_vec();
            let mut new_player_hp = player_hp;
            let mut new_last_combo = last_combo.cloned();
            if play.combo_type == "PASS" {
                new_player_hp -= 1;
                new_last_combo = last_combo.cloned();
            } else {
                for c in &play.cards {
                    if let Some(pos) = new_player.iter().position(|x| x.rank == c.rank && x.suit == c.suit) {
                        new_player.remove(pos);
                    }
                }
                new_last_combo = Some(play.clone());
            }
            // Our possible responses based on simulated hand
            let our_responses = estimate_opponent_responses(ai_hand, new_last_combo.as_ref());
            let mut eval = i32::MAX;
            for our_play in &our_responses {
                let (_ai_play, ai_eval) = minimax_search(
                    ai_hand,
                    &new_player,
                    ai_hp,
                    new_player_hp,
                    Some(our_play),
                    depth - 1,
                    true,
                    alpha,
                    beta,
                );
                eval = eval.min(ai_eval);
            }
            if eval < min_eval {
                min_eval = eval;
                best_play = Some(play.clone());
            }
            beta = beta.min(eval);
            if beta <= alpha {
                break;
            }
        }
        (best_play, min_eval)
    }
}

use pyo3::prelude::*;
use pyo3::types::PyString;
use rand::seq::SliceRandom;
use rayon::prelude::*;

use std::collections::HashMap;

#[derive(Clone, Debug, PartialEq, Eq, Hash, Serialize, serde::Deserialize)]
pub struct Card {
    pub rank: String,
    pub suit: String,
}

#[derive(Clone, Debug, Serialize, serde::Deserialize)]
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

#[pymodule]
fn mcts_rust(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(minimax_search_py, m)?)?;
    Ok(())
}

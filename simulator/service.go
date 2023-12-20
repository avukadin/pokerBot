package main

import (
	"encoding/json"
	"net/http"
)

func RunSimulation(w http.ResponseWriter, r *http.Request) {
	var params SimulationParams

	// Decode the JSON body into the params struct
	err := json.NewDecoder(r.Body).Decode(&params)
	if err != nil {
		// Handle error (e.g., respond with an error message)
		http.Error(w, err.Error(), http.StatusBadRequest)
		return
	}

	winRate := Simulate(&params)

	var response = SimulationResponse{
		WinRate : winRate,
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(response)
}

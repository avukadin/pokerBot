package main

import (
	"fmt"
	"net/http"

	"github.com/go-chi/chi"
	log "github.com/sirupsen/logrus"
)


func main(){

	log.SetReportCaller(true)
	var r *chi.Mux = chi.NewRouter()
	Handler(r)

	fmt.Println("Starting Poker Sim service...")
	err := http.ListenAndServe("localhost:8000", r)
  	if err != nil {
		log.Error(err)
 	}
}

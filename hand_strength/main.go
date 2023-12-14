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

	fmt.Println("Poker Sim Service running at localhost:8000/simulate")
	err := http.ListenAndServe("localhost:8000", r)
  	if err != nil {
		log.Error(err)
 	}
}

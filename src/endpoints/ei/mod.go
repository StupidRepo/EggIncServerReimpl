package ei

import (
	"github.com/gorilla/mux"
	"net/http"
)

func RegisterCoreEndpoints(r *mux.Router) {
	r.HandleFunc("/test", testHandler).Methods(http.MethodPost)
}

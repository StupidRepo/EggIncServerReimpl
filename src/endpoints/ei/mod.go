package ei

import (
	"github.com/gorilla/mux"
	"net/http"
)

func RegisterCoreEndpoints(r *mux.Router) {
	r.HandleFunc("/test", func(w http.ResponseWriter, r *http.Request) {
		w.Write([]byte("Hello, core!"))
	})
}

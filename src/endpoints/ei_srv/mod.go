package ei_srv

import (
	"github.com/gorilla/mux"
	"net/http"
)

func RegisterSubscriptionEndpoints(r *mux.Router) {
	r.HandleFunc("/test", func(w http.ResponseWriter, r *http.Request) {
		w.Write([]byte("Hello, srv!"))
	})
}

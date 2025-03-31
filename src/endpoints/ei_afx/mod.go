package ei_afx

import (
	"github.com/StupidRepo/NeoInc/src/middleware"
	"github.com/gorilla/mux"
	"net/http"
)

func RegisterArtifactEndpoints(r *mux.Router) {
	r.HandleFunc("/test", func(w http.ResponseWriter, r *http.Request) {
		neoIncDB := middleware.GetNeoIncDB(r)
		if neoIncDB != nil {
			w.Write([]byte("Hello, afx with DB!"))
		} else {
			w.Write([]byte("Hello, afx without DB!"))
		}
	})
}

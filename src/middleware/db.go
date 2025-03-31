package middleware

import (
	"context"
	"github.com/StupidRepo/NeoInc/src/database"
	"net/http"
)

type contextKey string

const dbContextKey = contextKey("NeoIncDB")

func WithNeoIncDB(next http.Handler, neoIncDB *database.NeoIncDB) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		if neoIncDB != nil {
			ctx := context.WithValue(r.Context(), dbContextKey, neoIncDB)
			r = r.WithContext(ctx)
		}
		next.ServeHTTP(w, r)
	})
}

func GetNeoIncDB(r *http.Request) *database.NeoIncDB {
	if db, ok := r.Context().Value(dbContextKey).(*database.NeoIncDB); ok {
		return db
	}
	return nil
}

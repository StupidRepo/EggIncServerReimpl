package main

import (
	"context"
	"github.com/StupidRepo/NeoInc/src/database"
	"github.com/StupidRepo/NeoInc/src/endpoints/ei"
	"github.com/StupidRepo/NeoInc/src/endpoints/ei_afx"
	"github.com/StupidRepo/NeoInc/src/endpoints/ei_srv"
	"github.com/StupidRepo/NeoInc/src/middleware"
	"github.com/gorilla/mux"
	"github.com/joho/godotenv"
	"go.mongodb.org/mongo-driver/v2/mongo"
	"go.mongodb.org/mongo-driver/v2/mongo/options"
	"go.mongodb.org/mongo-driver/v2/mongo/readpref"
	"log"
	"net/http"
	"os"
	"time"
)

func MakeRouter(neoIncDB *database.NeoIncDB) *mux.Router {
	baseRouter := mux.NewRouter()

	eiRouter := baseRouter.PathPrefix("/ei").Subrouter()
	eiAfxRouter := baseRouter.PathPrefix("/ei_afx").Subrouter()
	eiSrvRouter := baseRouter.PathPrefix("/ei_srv").Subrouter()

	ei.RegisterCoreEndpoints(eiRouter)
	ei_afx.RegisterArtifactEndpoints(eiAfxRouter)
	ei_srv.RegisterSubscriptionEndpoints(eiSrvRouter)

	baseRouter.Use(func(next http.Handler) http.Handler {
		return middleware.WithNeoIncDB(next, neoIncDB)
	})

	return baseRouter
}

func main() {
	var neoIncDB *database.NeoIncDB
	// load env
	err := godotenv.Load()
	if err != nil {
		log.Fatalln("Error loading .env file")
	}

	dbURL := os.Getenv("MONGO_URI")
	if dbURL == "" {
		log.Fatalln("MONGO_URI is not set!")
	}

	// connect to db
	log.Println("Attempting to connect to the DB at", dbURL)
	client, err := mongo.Connect(options.Client().ApplyURI(dbURL))
	defer func() {
		if err = client.Disconnect(context.TODO()); err != nil {
			log.Println("Failed to disconnect from MongoDB:", err)
		}
	}()
	if err != nil {
		log.Println("Failed to connect to MongoDB, some endpoints may not work:", err)
	}

	// ping for testing
	ctx, cancel := context.WithTimeout(context.Background(), 3*time.Second)
	defer cancel()

	if client != nil {
		err = client.Ping(ctx, readpref.Primary())
		if err != nil {
			log.Println("Failed to ping DB, some endpoints may not work:", err)
		} else {
			// make db object if connection is successful
			db := client.Database("NeoInc")
			neoIncDB = &database.NeoIncDB{
				Client: client,

				DB: db,

				Users:     db.Collection("Users"),
				Events:    db.Collection("Events"),
				Contracts: db.Collection("Contracts"),
			}
		}
	}

	// create router
	r := MakeRouter(neoIncDB)

	log.Println("Starting server on port 5000")

	// start server
	err = http.ListenAndServe(":5000", r)
	if err != nil {
		panic(err)
	}
}

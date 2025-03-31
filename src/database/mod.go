package database

import "go.mongodb.org/mongo-driver/v2/mongo"

type NeoIncDB struct {
	Client *mongo.Client

	DB *mongo.Database

	Users     *mongo.Collection
	Events    *mongo.Collection
	Contracts *mongo.Collection
}

package database

import (
	"context"
	"go.mongodb.org/mongo-driver/v2/bson"
	"go.mongodb.org/mongo-driver/v2/mongo"
)

// NeoIncDB is a wrapper around a MongoDB client and collections.
type NeoIncDB struct {
	Client *mongo.Client

	DB *mongo.Database

	Users     *mongo.Collection
	Events    *mongo.Collection
	Contracts *mongo.Collection
}

// GetAccountByNID retrieves an account by its NID.
func (db *NeoIncDB) GetAccountByNID(nid string) (*Account, error) {
	account := &Account{}
	err := db.Users.FindOne(context.Background(), bson.M{"_id": nid}).Decode(account)
	if err != nil {
		return nil, err
	}

	return account, nil
}

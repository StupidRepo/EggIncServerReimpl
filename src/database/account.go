package database

import (
	"github.com/StupidRepo/NeoInc/src/pb"
)

// Account represents a user account.
type Account struct {
	NID      string `bson:"_id"`
	Username string

	LatestBackup *pb.Backup // LatestBackup is the last cloud save that was sent from the client.
}

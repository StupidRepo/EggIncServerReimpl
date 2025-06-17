package utils

import (
	"encoding/base64"
	"github.com/StupidRepo/NeoInc/src/pb"
	"google.golang.org/protobuf/proto"
)

// ParseProtobuf parses a protobuf message from a byte slice.
// If parseAuthed is true, it will parse the byte slice as an AuthenticatedMessage, then parse the actual message.
func ParseProtobuf(data []byte, msg proto.Message, parseAuthed bool) error {
	if parseAuthed {
		var authMsg pb.AuthenticatedMessage

		err := proto.Unmarshal(data, &authMsg)
		if err != nil {
			return err
		}

		return proto.Unmarshal(authMsg.GetMessage(), msg)
	}

	return proto.Unmarshal(data, msg)
}

// MakeAuthenticatedMessage creates an AuthenticatedMessage from a protobuf message.
func MakeAuthenticatedMessage(msg proto.Message, useV2Hash bool) (*pb.AuthenticatedMessage, error) {
	data, err := proto.Marshal(msg)
	if err != nil {
		return nil, err
	}

	var hash string = ""
	if useV2Hash {
		hash = HashV2(data)
	} else {
		hash = HashV1(data)
	}

	return &pb.AuthenticatedMessage{
		Message: data,
		Code:    &hash,
	}, nil
}

// EncodeMessage encodes a protobuf message to a base64 string, which finalises the message for sending to the client.
func EncodeMessage(msg proto.Message) (*string, error) {
	// marshal the message
	data, err := proto.Marshal(msg)
	if err != nil {
		return nil, err
	}

	// base64 encode the message
	encoded := base64.StdEncoding.EncodeToString(data)
	return &encoded, nil
}

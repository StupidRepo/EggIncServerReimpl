package utils

import (
	"encoding/base64"
	"errors"
	"github.com/StupidRepo/NeoInc/src/pb"
	"google.golang.org/protobuf/proto"
	"net/http"
	"reflect"
)

// ErrInvalidHash is returned when an invalid hash is received.
var ErrInvalidHash = errors.New("received invalid hash")
var ErrNoData = errors.New("no data provided")

// ParseProtobufDataFromReq parses a protobuf message from a request.
func ParseProtobufDataFromReq(r *http.Request, msg proto.Message, parseAuthed bool) error {
	err := r.ParseForm()
	if err != nil {
		return err
	}

	// get 'data' value from form
	data := r.Form.Get("data")
	if data == "" {
		return ErrNoData
	}

	// decode the base64 data
	decoded, err := base64.StdEncoding.DecodeString(data)
	if err != nil {
		return err
	}

	// parse the protobuf message - if it's authed, check the hash
	if parseAuthed {
		var authMsg pb.AuthenticatedMessage

		err := ParseProtobuf(decoded, &authMsg, false)
		if err != nil {
			return err
		}

		// check the hash
		hash := authMsg.GetCode()
		if hash != HashV1(authMsg.GetMessage()) && hash != HashV2(authMsg.GetMessage()) {
			return ErrInvalidHash
		}

		return ParseProtobuf(authMsg.GetMessage(), msg, false)
	}

	return ParseProtobuf(decoded, msg, false)
}

// HandleError calls a function and automatically calls http.Error if an error is returned.
func HandleError(w http.ResponseWriter, function interface{}, args ...interface{}) bool {
	fn := reflect.ValueOf(function)
	if fn.Kind() != reflect.Func {
		http.Error(w, "Invalid function", http.StatusInternalServerError)
		return false
	}

	in := make([]reflect.Value, len(args))
	for i, arg := range args {
		in[i] = reflect.ValueOf(arg)
	}

	result := fn.Call(in)
	if len(result) > 0 && result[len(result)-1].Interface() != nil {
		if err, ok := result[len(result)-1].Interface().(error); ok {
			http.Error(w, err.Error(), http.StatusInternalServerError)
			return false
		}
	}

	return true
}

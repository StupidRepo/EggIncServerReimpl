package ei

import (
	"github.com/StupidRepo/NeoInc/src/pb"
	"github.com/StupidRepo/NeoInc/src/utils"
	"google.golang.org/protobuf/encoding/protojson"
	"net/http"
)

func testHandler(w http.ResponseWriter, r *http.Request) {
	var msg pb.BasicRequestInfo
	if !utils.HandleError(w, utils.ParseProtobufDataFromReq, r, &msg, false) {
		return
	}

	// write the msg back as json
	jsonData, err := protojson.Marshal(&msg)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	w.Write(jsonData)
}

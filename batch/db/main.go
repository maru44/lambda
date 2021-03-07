package main

import (
	"logs"
	"os"
	
	//"github.com/guregu/dynamo"
)

type Offer struct {
	Wanged string
	From string
	Datetime int
}

var (
	database = *dynamo.DB
)

func init() {
	region = os.Getenv("AWS_REGION")
}
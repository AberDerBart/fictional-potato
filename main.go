package main

import (
	"os"

	"github.com/rs/zerolog"
	"github.com/rs/zerolog/log"

	"github.com/vincent-petithory/mpdclient"
)

const schedulerChannelName = "scheduler"

func main() {
	log.Logger = log.Output(zerolog.ConsoleWriter{Out: os.Stdout})

	config, err := ParseConfig()
	if err != nil {
		log.Error().Err(err).Msg("failed to parse config")
		os.Exit(1)
	}

	log.Info().Msgf("connecting to %s on port %d", config.host, config.port)
	mpc, err := mpdclient.Connect(config.host, config.port)
	if err != nil {
		log.Error().Err(err).Msg("failed to connect")
		os.Exit(1)
	}
	defer mpc.Close()

	err = mpc.Subscribe(schedulerChannelName)
	if err != nil {
		log.Error().Err(err).Msg("failed to subscribe to channel")
		os.Exit(1)
	}

	log.Debug().Msgf("Listening on channel %s", schedulerChannelName)

	schedEvents := mpc.Idle("message")

	events := []*Event{}

	for {
		<-schedEvents.Ch
		msgs, err := mpc.ReadMessages()
		if err != nil {

			log.Error().Msgf("Failed to read message: %v", err)
		}

		for _, msg := range msgs {
			if msg.Channel == schedulerChannelName {
				newEvents, err := ExecCommand(mpc, events, msg.Message)
				if err != nil {
					log.Warn().Str("cmd", msg.Message).Err(err).Msg("failed to execute command")
				}

				if newEvents != nil {
					events = newEvents
				}
			}
		}
	}
}

Specification for USDB Syncer Separation

# Overview

Version: 1

This specification describes an interface for a binary to communicate with the main USDB Syncer.

# Interface

The syncer calls the binary on a separate thread. It communicates via stdin/stdout.

The main communication method is [JSON-RPC](https://www.jsonrpc.org/) 2.0 with line-delimited JSON messages. The binary must act as the JSON-RPC server. The syncer will act as the client.

# Methods

The binary must implement the following methods:

## `get_spec_version`

The version of this specification. The syncer will use this to determine if it can communicate with the binary.


## `exit`

Exit cleanly.

### Returns

- `version` (string): The version of this specification.

## `get_name`

The name of the binary, to be displayed for UI purposes.

### Returns

- `name` (string): The name of the binary.

## `get_available_models`

A list of available models to use for separation. Displayed in returned order. Default is first in list.

### Returns

- `models` (list of strings): The list of available models.

## `get_version`

Returns the version of the binary.

### Returns

- `version` (string): The version of the binary.

## `is_gpu_accelerated`

Whether the binary is GPU accelerated, for display/debug purposes. Should be computed on the fly based on available hardware.

### Returns

- `is_gpu_accelerated` (boolean): Whether the binary is GPU accelerated.

## `split`

Splits a video file into multiple files based on the audio track.

### Parameters

- `input_file`: The path to the input file.
- `output_dir`: The directory to output the split files to.
- `model`: The model to use for separation.

### Returns

- `output_vocals`: The path to the output vocals file.
- `output_instrumental`: The path to the output instrumental file.

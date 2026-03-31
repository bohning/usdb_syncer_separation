Specification for USDB Syncer Separation

# Overview

Version: 1

This specification describes an interface for a separation provider to communicate with the main USDB Syncer.

# Interface

The syncer calls the provider binary. It communicates via stdin/stdout. The provider may use stderr to output log or other debugging information.

The communication method is [JSON-RPC](https://www.jsonrpc.org/) 2.0 with line-delimited JSON messages. The provider runs the JSON-RPC server. The syncer acts as the client. To implement this spec, the provider must implement _all_ methods described in the "Methods" section. The provider may implement additional methods for any reason, but the syncer will only call the specified methods.

## Error Handling

If an error occurs, the provider should return a JSON-RPC error response.

# Methods

The binary must implement the following methods:

## `get_spec_version`

The version of this specification. The syncer will use this to determine if it can communicate with the provider.

### Returns

- `version` (string): The version of this specification.

## `exit`

Exit cleanly.

## `get_name`

The name of the binary, to be displayed for UI purposes.

### Returns

- `name` (string): The name of the binary.

## `get_available_models`

A dictionary of available models to use for separation, with model name as key and model display name as value. Must not change at runtime. Displayed in returned order. Default is first in list.

### Returns

- `models` (dict of string, string): name, display name pairs

## `get_version`

Returns the version of the binary for display purposes.

### Returns

- `version` (string): The version of the binary.

## `is_gpu_accelerated`

Whether the binary is GPU accelerated, for display/debug purposes. Should be computed on the fly based on available hardware.

### Returns

- `is_gpu_accelerated` (boolean): Whether the provider is GPU accelerated.

## `split`

Splits a video file into multiple files based on the audio track.

### Parameters

- `input_file`: The path to the input file.
- `output_dir`: The directory to output the split files to.
- `model`: The model to use for separation. Guaranteed to be one of the keys returned by `get_available_models`.

### Returns

- `output_vocals`: The path to the output vocals file.
- `output_instrumental`: The path to the output instrumental file.

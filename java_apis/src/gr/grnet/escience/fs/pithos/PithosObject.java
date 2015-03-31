/**
 * Licensed to the Apache Software Foundation (ASF) under one
 * or more contributor license agreements.  See the NOTICE file
 * distributed with this work for additional information
 * regarding copyright ownership.  The ASF licenses this file
 * to you under the Apache License, Version 2.0 (the
 * "License"); you may not use this file except in compliance
 * with the License.  You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

package gr.grnet.escience.fs.pithos;

import java.io.IOException;
import java.io.InputStream;

/**
 * Holds file metadata including type (regular file, or directory), and the list
 * of blocks that are pointers to the data.
 */

public class PithosObject {

	private PithosObjectBlock[] objectBlocks;

	/** Create a Pithos Object **/
	public PithosObject(PithosObjectBlock[] _blocks) {
		// - Check if try to create Object by using Pithos container
		if (_blocks == null) {
			throw new IllegalArgumentException(
					"A directory cannot contain blocks.");
		}

		// - Initialize blocks of the object
		this.objectBlocks = _blocks;
	}

	public PithosObjectBlock[] getPithosObjectBlocks() {
		return objectBlocks;
	}

	/****
	 * Serialize a Pithos Object so as to perform various actions, such as to
	 * copy it to the pithos dfs
	 * 
	 * @return
	 * @throws IOException
	 */
	public InputStream serialize() throws IOException {
		// TODO: add either method from Pithos REST CLient or write another
		// specific functionality

		return null;
	}

	/***
	 * Deserialize a Pithos Object that is received by the pithos dfs
	 * 
	 * @param {inputStreamForObject: the inputstream that correspnds to
	 *        PithosObject bytes}
	 * @return
	 * @throws IOException
	 */
	public static PithosObject deserialize(InputStream inputStreamForObject)
			throws IOException {
		// - Check if the incoming data is null
		if (inputStreamForObject == null) {
			return null;
		}
		// TODO: add either method from Pithos REST CLient or write another
		// specific functionality
		return null;
	}

}

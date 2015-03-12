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

package org.apache.hadoop.fs.pithos;

import java.io.ByteArrayInputStream;
import java.io.ByteArrayOutputStream;
import java.io.DataInputStream;
import java.io.DataOutputStream;
import java.io.IOException;
import java.io.InputStream;

import org.apache.hadoop.io.IOUtils;

/**
 * Holds file metadata including type (regular file, or directory), and the list
 * of blocks that are pointers to the data.
 */

public class PithosObject {

	enum PithosFileType {
		CONTAINER, OBJECT
	}

	public static final PithosFileType[] FILE_TYPES = {
			PithosFileType.CONTAINER, PithosFileType.OBJECT };

	public static final PithosObject PITHOS_CONTAINER = new PithosObject(
			PithosFileType.CONTAINER, null);

	private PithosFileType pithosfileType;
	private PithosObjectBlock[] objectBlocks;

	/** Create a Pithos Object **/
	public PithosObject(PithosFileType _pithosfileType,
			PithosObjectBlock[] _blocks) {
		// - Initialize the selected pithos file type
		this.pithosfileType = _pithosfileType;

		// - Check if try to create Object by using Pithos container
		if ((isPithosContainer()) && (_blocks != null)) {
			throw new IllegalArgumentException(
					"A directory cannot contain blocks.");
		}

		// - initialize blocks of the object
		this.objectBlocks = _blocks;
	}

	public PithosObjectBlock[] getPithosObjectBlocks() {
		return objectBlocks;
	}

	public PithosFileType getFileType() {
		return pithosfileType;
	}

	public boolean isPithosContainer() {
		return getFileType() == PithosFileType.CONTAINER;
	}

	public boolean isPithosObject() {
		return getFileType() == PithosFileType.OBJECT;
	}

	public long getSerializedLength() {
		/** In order to represent it into KBs **/
		if (getPithosObjectBlocks() != null) {
			return 1L + (4 + getPithosObjectBlocks().length * 16);
		} else {
			return 0;
		}
	}

	/****
	 * Serialize a Pithos Object so as to perform various actions, such as to
	 * copy it to the pithos dfs
	 * 
	 * @return
	 * @throws IOException
	 */
	public InputStream serialize() throws IOException {

		// - Create native bytes array for the streaming object data that
		// corresponds to blocks
		ByteArrayOutputStream bytes = new ByteArrayOutputStream();
		// - Create the outpustream for the object
		DataOutputStream out = new DataOutputStream(bytes);

		try {
			// - Write to the output stream the type of the serialized file type
			out.writeByte(pithosfileType.ordinal());

			// - Check if the serialized entity is Pithos OBject
			if (isPithosObject()) {
				// - Get the number of the blocks that constitute the Object
				int pithosObjectBlocksNumber = getPithosObjectBlocks().length;

				// Writes the number of blocks to the underlying output stream
				// as four bytes, high byte first.
				out.writeInt(pithosObjectBlocksNumber);

				// - Stream the data for each block by adding the Block Hash and
				// the block length
				for (int i = 0; i < objectBlocks.length; i++) {
					out.writeLong(objectBlocks[i].getBlockHash());
					out.writeLong(objectBlocks[i].getBlockLength());
				}
			}

			// - Flush and close the data output stream
			out.flush();
			out.close();
			out = null;

		} finally {
			IOUtils.closeStream(out);
		}
		return new ByteArrayInputStream(bytes.toByteArray());
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

		// - Create data input stream for the deseralization of data from the input stream
		DataInputStream objectData = new DataInputStream(inputStreamForObject);

		// - Get the file type of the received input stream that corresponds to
		// a Pithos Object
		PithosFileType pithosfileType = PithosObject.FILE_TYPES[objectData.readByte()];

		// - Perform the corresponding action based on the type of the received
		// object
		switch (pithosfileType) {
		// - Return the container
		case CONTAINER:
			inputStreamForObject.close();
			return PithosObject.PITHOS_CONTAINER;
			
		// - Return the pithos object by composing it through the received
		// blocks from the input stream
		case OBJECT:
			// - Get the number of blocks that compose the object
			int numBlocks = objectData.readInt();

			// - Create an Array for the storage of the blocks
			PithosObjectBlock[] blocks = new PithosObjectBlock[numBlocks];

			// - Get the blocks of the object
			for (int i = 0; i < numBlocks; i++) {
				// - Read block metadata
				long blockHash = objectData.readLong();
				long blockLength = objectData.readLong();
				// - Create and add new block of the pithos object into the
				// array of blocks for the current object
				blocks[i] = new PithosObjectBlock(blockHash, blockLength);
			}

			// - Close the stream
			inputStreamForObject.close();
			
			//- Return the structured object
			return new PithosObject(pithosfileType, blocks);
		default:
			throw new IllegalArgumentException(
					"Cannot deserialize the pithos object.");
		}
	}

}

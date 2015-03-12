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

import java.io.File;
import java.io.IOException;
import java.net.URI;
import java.util.Set;

import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.fs.Path;


public interface PithosSystemStore {
  
  void initialize(URI uri, Configuration conf) throws IOException;
  String getVersion() throws IOException;

  void storePithosNode(Path path, PithosObject pithosNode) throws IOException;
  void storePithosBlock(PithosObjectBlock pithosBlock, File file) throws IOException;
  
  boolean inodeExists(Path path) throws IOException;
  boolean blockExists(long blockId) throws IOException;

  PithosObject retrievePithosNode(Path path) throws IOException;
  File retrievePithosBlock(PithosObjectBlock pithosBlock, long byteRangeStart) throws IOException;

  void deleteINode(Path path) throws IOException;
  void deleteBlock(PithosObjectBlock pithosBlock) throws IOException;

  Set<Path> listSubPaths(Path path) throws IOException;
  Set<Path> listDeepSubPaths(Path path) throws IOException;

}

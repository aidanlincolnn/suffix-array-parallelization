// Copyright 2010 Google Inc.
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//      http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.
//
// ---
// Author: David Eger

#ifndef RMQ_H_
#define RMQ_H_

// An interface for RangeMinimumQuery algorithms:
//
// Given an integer array of values,
//    What index k >= i and k < j minimizes arr[k]?
//
// There are implementations for RMQ which, given some preprocessing time,
// can answer such queries using only two lookups.
class RangeMinimumQuery {
 public:
  // We presume arr will outlive us.
  RangeMinimumQuery(const int *arr, int n) : arr_(arr), n_(n) {}
  virtual ~RangeMinimumQuery() {}

  // Return the index m in [i,j) that minimizes arr[m].
  virtual int Query(int i, int j) const = 0;

 protected:
  const int *arr_;
  const int n_;
};


#endif  // RMQ_H_

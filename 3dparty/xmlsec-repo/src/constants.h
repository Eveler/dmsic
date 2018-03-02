// Copyright (c) 2017 Ryan Leckey
// THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
// IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
// FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
// AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
// LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
// OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
// SOFTWARE.

#ifndef __PYXMLSEC_CONSTANTS_H__
#define __PYXMLSEC_CONSTANTS_H__

#include "platform.h"

#include <xmlsec/xmlsec.h>
#include <xmlsec/crypto.h>

typedef struct {
    PyObject_HEAD
    xmlSecTransformId id;
} PyXmlSec_Transform;

typedef struct {
    PyObject_HEAD
    xmlSecKeyDataId id;
} PyXmlSec_KeyData;

extern PyTypeObject* PyXmlSec_TransformType;
extern PyTypeObject* PyXmlSec_KeyDataType;

#endif //__PYXMLSEC_CONSTANTS_H__

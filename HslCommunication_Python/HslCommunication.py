import string
import uuid
import socket
import struct
import threading

class StringResources:
	'''系统的资源类'''
	@staticmethod
	def ConnectedFailed():
		return "连接失败"
	@staticmethod
	def UnknownError():
		return "未知错误"
	@staticmethod
	def ErrorCode():
		return "错误代号"
	@staticmethod
	def TextDescription():
		return "文本描述"
	@staticmethod
	def ExceptionMessage():
		return "错误信息："
	@staticmethod
	def ExceptionStackTrace():
		return "错误堆栈："
	@staticmethod
	def ExceptopnTargetSite():
		return "错误方法："
	@staticmethod
	def ExceprionCustomer():
		return "用户自定义方法出错："
	@staticmethod
	def TokenCheckFailed():
		return "令牌检查错误。"
	@staticmethod
	def SuccessText():
		return "Success"


class OperateResult:
	'''结果对象类，可以携带额外的数据信息'''
	# 是否成功的标志
	IsSuccess = False
	# 操作返回的错误消息
	Message = StringResources.SuccessText()
	# 错误码
	ErrorCode = 0
	# 返回显示的文本
	def ToMessageShowString(self):
		'''获取错误代号及文本描述'''
		return StringResources.ErrorCode() + ":" + str(self.ErrorCode) + "\r\n" + StringResources.TextDescription() + ":" + self.Message
	def CopyErrorFromOther(self, result):
		'''从另一个结果类中拷贝错误信息'''
		if result != None:
			self.ErrorCode = result.ErrorCode
			self.Message = result.Message
	@staticmethod
	def CreateFailedResult(msg):
		'''创建一个失败的结果对象'''
		failed = OperateResult()
		failed.Message = msg
		return failed
	@staticmethod
	def CreateFromFailedResult(result):
		'''创建一个失败的结果对象'''
		failed = OperateResult()
		failed.ErrorCode = result.ErrorCode
		failed.Message = result.Message
		return failed
	@staticmethod
	def CreateSuccessResult(Content1=None,Content2=None,Content3=None,Content4=None,Content5=None,Content6=None,Content7=None,Content8=None,Content9=None,Content10=None):
		'''创建一个成功的对象'''
		success = OperateResult()
		success.IsSuccess = True
		success.Message = StringResources.SuccessText()
		if(Content2 == None and Content3 == None and Content4 == None and Content5 == None and Content6 == None and Content7 == None and Content8 == None and Content9 == None and Content10 == None) :
			success.Content = Content1
		else:
			success.Content1 = Content1
			success.Content2 = Content2
			success.Content3 = Content3
			success.Content4 = Content4
			success.Content5 = Content5
			success.Content6 = Content6
			success.Content7 = Content7
			success.Content8 = Content8
			success.Content9 = Content9
			success.Content10 = Content10
		return success

class SoftIncrementCount:
	'''一个简单的不持久化的序号自增类，采用线程安全实现，并允许指定最大数字，到达后清空从指定数开始'''
	start = 0
	current = 0
	maxValue = 100000000000000000000000000
	hybirdLock = threading.Lock()
	def __init__(self, maxValue, start):
		'''实例化一个自增信息的对象，包括最大值'''
		self.maxValue = maxValue
		self.start = start
	def GetCurrentValue( self ):
		'''获取自增信息'''
		value = 0
		self.hybirdLock.acquire()
		value = self.current
		self.current = self.current + 1
		if self.current > self.maxValue:
			self.current = 0
		self.hybirdLock.release()
		return value
	

class INetMessage:
	'''数据消息的基本基类'''
	def ProtocolHeadBytesLength(self):
		'''协议头数据长度，也即是第一次接收的数据长度'''
		return 0
	def GetContentLengthByHeadBytes(self):
		'''二次接收的数据长度'''
		return 0
	def CheckHeadBytesLegal(self,token):
		'''令牌检查是否成功'''
		return False
	def GetHeadBytesIdentity(self):
		'''获取头子节里的消息标识'''
		return 0

	HeadBytes = bytes(0)
	ContentBytes = bytes(0)
	SendBytes = bytes(0)

class S7Message (INetMessage):
	'''西门子s7协议的消息接收规则'''
	def ProtocolHeadBytesLength(self):
		'''协议头数据长度，也即是第一次接收的数据长度'''
		return 4
	def GetContentLengthByHeadBytes(self):
		'''二次接收的数据长度'''
		if super().HeadBytes != None:
			return super().HeadBytes[2]*256 + super().HeadBytes[3]-4
		else:
			return 0
	def CheckHeadBytesLegal(self,token):
		'''令牌检查是否成功'''
		if super().HeadBytes != None:
			if( super().HeadBytes[0] == 0x03 and super().HeadBytes[1] == 0x00 ):
				return True
			else:
				return False
		else:
			return False

class ModbusTcpMessage (INetMessage):
	'''Modbus-Tcp协议的信息'''
	def ProtocolHeadBytesLength(self):
		'''协议头数据长度，也即是第一次接收的数据长度'''
		return 6
	def GetContentLengthByHeadBytes(self):
		'''二次接收的数据长度'''
		if super().HeadBytes != None:
			return super().HeadBytes[4] * 256 + super().HeadBytes[5]
		else:
			return 0
	def CheckHeadBytesLegal(self,token):
		'''令牌检查是否成功'''
		return True
	def GetHeadBytesIdentity(self):
		'''获取头子节里的消息标识'''
		return super().HeadBytes[0] * 256 + super().HeadBytes[1]


class ByteTransform:
	'''数据转换类的基础，提供了一些基础的方法实现.'''
	def TransBool(self, buffer, index ):
		'''将buffer数组转化成bool对象'''
		return ((buffer[index] & 0x01) == 0x01)
	def TransBoolArray(self, buffer, index, length ):
		'''将buffer数组转化成bool数组对象，需要转入索引，长度'''
		data = bytearray(length)
		for i in range(length):
			data[i]=buffer[i+index]
		return SoftBasic.ByteToBoolArray( data, length * 8 )

	def TransByte( self, buffer, index ):
		'''将buffer中的字节转化成byte对象，需要传入索引'''
		return buffer[index]
	def TransByteArray( self, buffer, index, length ):
		'''将buffer中的字节转化成byte数组对象，需要传入索引'''
		data = bytearray(length)
		for i in range(length):
			data[i]=buffer[i+index]
		return data

	def TransInt16( self, buffer, index ):
		'''从缓存中提取short结果'''
		data = self.TransByteArray(buffer,index,2)
		return struct.unpack('<h',data)[0]
	def TransInt16Array( self, buffer, index, length ):
		'''从缓存中提取short数组结果'''
		tmp = []
		for i in range(length):
			tmp.append( self.TransInt16( buffer, index + 2 * i ))
		return tmp

	def TransUInt16(self, buffer, index ):
		'''从缓存中提取ushort结果'''
		data = self.TransByteArray(buffer,index,2)
		return struct.unpack('<H',data)[0]
	def TransUInt16Array(self, buffer, index, length ):
		'''从缓存中提取ushort数组结果'''
		tmp = []
		for i in range(length):
			tmp.append( self.TransUInt16( buffer, index + 2 * i ))
		return tmp
	
	def TransInt32(self, buffer, index ):
		'''从缓存中提取int结果'''
		data = self.TransByteArray(buffer,index,4)
		return struct.unpack('<i',data)[0]
	def TransInt32Array(self, buffer, index, length ):
		'''从缓存中提取int数组结果'''
		tmp = []
		for i in range(length):
			tmp.append( self.TransInt32( buffer, index + 4 * i ))
		return tmp

	def TransUInt32(self, buffer, index ):
		'''从缓存中提取uint结果'''
		data = self.TransByteArray(buffer,index,4)
		return struct.unpack('<I',data)[0]
	def TransUInt32Array(self, buffer, index, length ):
		'''从缓存中提取uint数组结果'''
		tmp = []
		for i in range(length):
			tmp.append( self.TransUInt32( buffer, index + 4 * i ))
		return tmp
	
	def TransInt64(self, buffer, index ):
		'''从缓存中提取long结果'''
		data = self.TransByteArray(buffer,index,8)
		return struct.unpack('<q',data)[0]
	def TransInt64Array(self, buffer, index, length):
		'''从缓存中提取long数组结果'''
		tmp = []
		for i in range(length):
			tmp.append( self.TransInt64( buffer, index + 8 * i ))
		return tmp
	
	def TransUInt64(self, buffer, index ):
		'''从缓存中提取ulong结果'''
		data = self.TransByteArray(buffer,index,8)
		return struct.unpack('<Q',data)[0]
	def TransUInt64Array(self, buffer, index, length):
		'''从缓存中提取ulong数组结果'''
		tmp = []
		for i in range(length):
			tmp.append( self.TransUInt64( buffer, index + 8 * i ))
		return tmp
	
	def TransSingle(self, buffer, index ):
		'''从缓存中提取float结果'''
		data = self.TransByteArray(buffer,index,4)
		return struct.unpack('<f',data)[0]
	def TransSingleArray(self, buffer, index, length):
		'''从缓存中提取float数组结果'''
		tmp = []
		for i in range(length):
			tmp.append( self.TransSingle( buffer, index + 4 * i ))
		return tmp
	
	def TransDouble(self, buffer, index ):
		'''从缓存中提取double结果'''
		data = self.TransByteArray(buffer,index,8)
		return struct.unpack('<d',data)[0]
	def TransDoubleArray(self, buffer, index, length):
		'''从缓存中提取double数组结果'''
		tmp = []
		for i in range(length):
			tmp.append( self.TransSingle( buffer, index + 8 * i ))
		return tmp

	def TransString( self, buffer, index, length, encoding ):
		'''从缓存中提取string结果，使用指定的编码'''
		data = self.TransByteArray(buffer,index,length)
		return data.decode(encoding)

	def BoolArrayTransByte(self, values):
		'''bool数组变量转化缓存数据，需要传入bool数组'''
		if (values == None): return None
		return SoftBasic.BoolArrayToByte( values )
	def BoolTransByte(self, value):
		'''bool变量转化缓存数据，需要传入bool值'''
		return self.BoolArrayTransByte([value])

	def ByteTransByte(self, value ):
		'''byte变量转化缓存数据，需要传入byte值'''
		buffer = bytearray(1)
		buffer[0] = value
		return buffer

	def Int16ArrayTransByte(self, values ):
		'''short数组变量转化缓存数据，需要传入short数组'''
		if (values == None) : return None
		buffer = bytearray(len(values) * 2)
		for i in range(len(values)):
			buffer[(i*2): (i*2+2)] = struct.pack('<h',values[i])
		return buffer
	def Int16TransByte(self, value ):
		'''short数组变量转化缓存数据，需要传入short值'''
		return self.Int16ArrayTransByte([value])

	def UInt16ArrayTransByte(self, values ):
		'''ushort数组变量转化缓存数据，需要传入ushort数组'''
		if (values == None) : return None
		buffer = bytearray(len(values) * 2)
		for i in range(len(values)):
			buffer[(i*2): (i*2+2)] = struct.pack('<H',values[i])
		return buffer
	def UInt16TransByte(self, value ):
		'''ushort变量转化缓存数据，需要传入ushort值'''
		return self.UInt16ArrayTransByte([value])

	def Int32ArrayTransByte(self, values ):
		'''int数组变量转化缓存数据，需要传入int数组'''
		if (values == None) : return None
		buffer = bytearray(len(values) * 4)
		for i in range(len(values)):
			buffer[(i*4): (i*4+4)] = struct.pack('<i',values[i])
		return buffer
	def Int32TransByte(self, value ):
		'''int变量转化缓存数据，需要传入int值'''
		return self.Int32ArrayTransByte([value])

	def UInt32ArrayTransByte(self, values ):
		'''uint数组变量转化缓存数据，需要传入uint数组'''
		if (values == None) : return None
		buffer = bytearray(len(values) * 4)
		for i in range(len(values)):
			buffer[(i*4): (i*4+4)] = struct.pack('<I',values[i])
		return buffer
	def UInt32TransByte(self, value ):
		'''uint变量转化缓存数据，需要传入uint值'''
		return self.UInt32ArrayTransByte([value])

	def Int64ArrayTransByte(self, values ):
		'''long数组变量转化缓存数据，需要传入long数组'''
		if (values == None) : return None
		buffer = bytearray(len(values) * 8)
		for i in range(len(values)):
			buffer[(i*8): (i*8+8)] = struct.pack('<q',values[i])
		return buffer
	def Int64TransByte(self, value ):
		'''long变量转化缓存数据，需要传入long值'''
		return self.Int64ArrayTransByte([value])

	def UInt64ArrayTransByte(self, values ):
		'''ulong数组变量转化缓存数据，需要传入ulong数组'''
		if (values == None) : return None
		buffer = bytearray(len(values) * 8)
		for i in range(len(values)):
			buffer[(i*8): (i*8+8)] = struct.pack('<Q',values[i])
		return buffer
	def UInt64TransByte(self, value ):
		'''ulong变量转化缓存数据，需要传入ulong值'''
		return self.UInt64ArrayTransByte([value])

	def FloatArrayTransByte(self, values ):
		'''float数组变量转化缓存数据，需要传入float数组'''
		if (values == None) : return None
		buffer = bytearray(len(values) * 4)
		for i in range(len(values)):
			buffer[(i*4): (i*4+4)] = struct.pack('<f',values[i])
		return buffer
	def FloatTransByte(self, value ):
		'''float变量转化缓存数据，需要传入float值'''
		return self.FloatArrayTransByte([value])

	def DoubleArrayTransByte(self, values ):
		'''double数组变量转化缓存数据，需要传入double数组'''
		if (values == None) : return None
		buffer = bytearray(len(values) * 8)
		for i in range(len(values)):
			buffer[(i*8): (i*8+8)] = struct.pack('<d',values[i])
		return buffer
	def DoubleTransByte(self, value ):
		'''double变量转化缓存数据，需要传入double值'''
		return self.DoubleArrayTransByte([value])

	def StringTransByte(self, value, encoding ):
		'''使用指定的编码字符串转化缓存数据，需要传入string值及编码信息'''
		return value.encode(encoding)

class RegularByteTransform(ByteTransform):
	'''常规的字节转换类'''
	def __init__(self):
		return

class ReverseBytesTransform(ByteTransform):
	'''字节倒序的转换类'''
	def TransInt16(self, buffer, index ):
		'''从缓存中提取short结果'''
		data = self.TransByteArray(buffer,index,2)
		return struct.unpack('>h',data)[0]
	def TransUInt16(self, buffer, index ):
		'''从缓存中提取ushort结果'''
		data = self.TransByteArray(buffer,index,2)
		return struct.unpack('>H',data)[0]
	def TransInt32(self, buffer, index ):
		'''从缓存中提取int结果'''
		data = self.TransByteArray(buffer,index,4)
		return struct.unpack('>i',data)[0]
	def TransUInt32(self, buffer, index ):
		'''从缓存中提取uint结果'''
		data = self.TransByteArray(buffer,index,4)
		return struct.unpack('>I',data)[0]
	def TransInt64(self, buffer, index ):
		'''从缓存中提取long结果'''
		data = self.TransByteArray(buffer,index,8)
		return struct.unpack('>q',data)[0]
	def TransUInt64(self, buffer, index ):
		'''从缓存中提取ulong结果'''
		data = self.TransByteArray(buffer,index,8)
		return struct.unpack('>Q',data)[0]
	def TransSingle(self, buffer, index ):
		'''从缓存中提取float结果'''
		data = self.TransByteArray(buffer,index,4)
		return struct.unpack('>f',data)[0]
	def TransDouble(self, buffer, index ):
		'''从缓存中提取double结果'''
		data = self.TransByteArray(buffer,index,8)
		return struct.unpack('>d',data)[0]
	
	def Int16ArrayTransByte(self, values ):
		'''short数组变量转化缓存数据，需要传入short数组 -> bytearray'''
		if (values == None) : return None
		buffer = bytearray(len(values) * 2)
		for i in range(len(values)):
			buffer[(i*2): (i*2+2)] = struct.pack('>h',values[i])
		return buffer
	def UInt16ArrayTransByte(self, values ):
		'''ushort数组变量转化缓存数据，需要传入ushort数组 -> bytearray'''
		if (values == None) : return None
		buffer = bytearray(len(values) * 2)
		for i in range(len(values)):
			buffer[(i*2): (i*2+2)] = struct.pack('>H',values[i])
		return buffer
	def Int32ArrayTransByte(self, values ):
		'''int数组变量转化缓存数据，需要传入int数组 -> bytearray'''
		if (values == None) : return None
		buffer = bytearray(len(values) * 4)
		for i in range(len(values)):
			buffer[(i*4): (i*4+4)] = struct.pack('>i',values[i])
		return buffer
	def UInt32ArrayTransByte(self, values ):
		'''uint数组变量转化缓存数据，需要传入uint数组 -> bytearray'''
		if (values == None) : return None
		buffer = bytearray(len(values) * 4)
		for i in range(len(values)):
			buffer[(i*4): (i*4+4)] = struct.pack('>I',values[i])
		return buffer
	def Int64ArrayTransByte(self, values ):
		'''long数组变量转化缓存数据，需要传入long数组 -> bytearray'''
		if (values == None) : return None
		buffer = bytearray(len(values) * 8)
		for i in range(len(values)):
			buffer[(i*8): (i*8+8)] = struct.pack('>q',values[i])
		return buffer
	def UInt64ArrayTransByte(self, values ):
		'''ulong数组变量转化缓存数据，需要传入ulong数组 -> bytearray'''
		if (values == None) : return None
		buffer = bytearray(len(values) * 8)
		for i in range(len(values)):
			buffer[(i*8): (i*8+8)] = struct.pack('>Q',values[i])
		return buffer
	def FloatArrayTransByte(self, values ):
		'''float数组变量转化缓存数据，需要传入float数组 -> bytearray'''
		if (values == None) : return None
		buffer = bytearray(len(values) * 4)
		for i in range(len(values)):
			buffer[(i*4): (i*4+4)] = struct.pack('>f',values[i])
		return buffer
	def DoubleArrayTransByte(self, values ):
		'''double数组变量转化缓存数据，需要传入double数组 -> bytearray'''
		if (values == None) : return None
		buffer = bytearray(len(values) * 8)
		for i in range(len(values)):
			buffer[(i*8): (i*8+8)] = struct.pack('>d',values[i])
		return buffer

class ReverseWordTransform(ByteTransform):
	'''按照字节错位的数据转换类'''
	def ReverseBytesByWord( self,buffer, index, length, isReverse = False):
		'''按照字节错位的方法 -> bytearray'''
		if buffer == None: return None
		data = super().TransByteArray(buffer,index,length)
		for i in range(len(data)//2):
			data[i*2+0],data[i*2+1]= data[i*2+1],data[i*2+0]
		if isReverse:
			if len(data)==4:
				data[0],data[1],data[2],data[3] = data[2],data[3],data[0],data[1]
			elif len(data) == 8:
				data[0],data[1],data[2],data[3],data[4],data[5],data[6],data[7] = data[6],data[7],data[4],data[5],data[2],data[3],data[0],data[1]
		return data
	def ReverseAllBytesByWord( self, buffer , isReverse = False ):
		'''按照字节错位的方法 -> bytearray'''
		return self.ReverseBytesByWord(buffer,0,len(buffer),isReverse)
	IsMultiWordReverse = False
	IsStringReverse = False
	def TransInt16( self, buffer, index ):
		'''从缓存中提取short结果'''
		data = self.ReverseBytesByWord(buffer,index,2)
		return struct.unpack('<h',data)[0]
	def TransUInt16(self, buffer, index ):
		'''从缓存中提取ushort结果'''
		data = self.ReverseBytesByWord(buffer,index,2)
		return struct.unpack('<H',data)[0]
	def TransInt32(self, buffer, index ):
		'''从缓存中提取int结果'''
		data = self.ReverseBytesByWord(buffer,index,4,self.IsMultiWordReverse)
		return struct.unpack('<i',data)[0]
	def TransUInt32(self, buffer, index ):
		'''从缓存中提取uint结果'''
		data = self.ReverseBytesByWord(buffer,index,4,self.IsMultiWordReverse)
		return struct.unpack('<I',data)[0]
	def TransInt64(self, buffer, index ):
		'''从缓存中提取long结果'''
		data = self.ReverseBytesByWord(buffer,index,8,self.IsMultiWordReverse)
		return struct.unpack('<q',data)[0]
	def TransUInt64(self, buffer, index ):
		'''从缓存中提取ulong结果'''
		data = self.ReverseBytesByWord(buffer,index,8,self.IsMultiWordReverse)
		return struct.unpack('<Q',data)[0]
	def TransSingle(self, buffer, index ):
		'''从缓存中提取float结果'''
		data = self.ReverseBytesByWord(buffer,index,4,self.IsMultiWordReverse)
		return struct.unpack('<f',data)[0]
	def TransDouble(self, buffer, index ):
		'''从缓存中提取double结果'''
		data = self.ReverseBytesByWord(buffer,index,8,self.IsMultiWordReverse)
		return struct.unpack('<d',data)[0]
	def TransString( self, buffer, index, length, encoding ):
		'''从缓存中提取string结果，使用指定的编码'''
		data = self.TransByteArray(buffer,index,length)
		if self.IsStringReverse:
			return self.ReverseAllBytesByWord(data,False).decode(encoding)
		else:
			return data.decode(encoding)
	
	def Int16ArrayTransByte(self, values ):
		'''short数组变量转化缓存数据，需要传入short数组'''
		buffer = super().Int16ArrayTransByte(values)
		return self.ReverseAllBytesByWord(buffer,False)
	def UInt16ArrayTransByte(self, values ):
		'''ushort数组变量转化缓存数据，需要传入ushort数组'''
		buffer = super().UInt16ArrayTransByte(values)
		return self.ReverseAllBytesByWord(buffer,False)
	def Int32ArrayTransByte(self, values ):
		'''int数组变量转化缓存数据，需要传入int数组'''
		if (values == None) : return None
		buffer = bytearray(len(values) * 4)
		for i in range(len(values)):
			buffer[(i*4): (i*4+4)] = self.ReverseAllBytesByWord(struct.pack('<i',values[i]),self.IsMultiWordReverse)
		return buffer
	def UInt32ArrayTransByte(self, values ):
		'''uint数组变量转化缓存数据，需要传入uint数组'''
		if (values == None) : return None
		buffer = bytearray(len(values) * 4)
		for i in range(len(values)):
			buffer[(i*4): (i*4+4)] = self.ReverseAllBytesByWord(struct.pack('<I',values[i]),self.IsMultiWordReverse)
		return buffer
	def Int64ArrayTransByte(self, values ):
		'''long数组变量转化缓存数据，需要传入long数组'''
		if (values == None) : return None
		buffer = bytearray(len(values) * 8)
		for i in range(len(values)):
			buffer[(i*8): (i*8+8)] = self.ReverseAllBytesByWord(struct.pack('<q',values[i]),self.IsMultiWordReverse)
		return buffer
	def UInt64ArrayTransByte(self, values ):
		'''ulong数组变量转化缓存数据，需要传入ulong数组'''
		if (values == None) : return None
		buffer = bytearray(len(values) * 8)
		for i in range(len(values)):
			buffer[(i*8): (i*8+8)] = self.ReverseAllBytesByWord(struct.pack('<Q',values[i]),self.IsMultiWordReverse)
		return buffer
	def FloatArrayTransByte(self, values ):
		'''float数组变量转化缓存数据，需要传入float数组'''
		if (values == None) : return None
		buffer = bytearray(len(values) * 4)
		for i in range(len(values)):
			buffer[(i*4): (i*4+4)] = self.ReverseAllBytesByWord(struct.pack('<f',values[i]),self.IsMultiWordReverse)
		return buffer
	def DoubleArrayTransByte(self, values ):
		'''double数组变量转化缓存数据，需要传入double数组'''
		if (values == None) : return None
		buffer = bytearray(len(values) * 8)
		for i in range(len(values)):
			buffer[(i*8): (i*8+8)] = self.ReverseAllBytesByWord(struct.pack('<d',values[i]),self.IsMultiWordReverse)
		return buffer
	def StringTransByte(self, value, encoding ):
		'''使用指定的编码字符串转化缓存数据，需要传入string值及编码信息'''
		buffer = value.encode(encoding)
		buffer = SoftBasic.BytesArrayExpandToLengthEven(buffer)
		if self.IsStringReverse:
			return self.ReverseAllBytesByWord( buffer, False )
		else:
			return buffer

class ByteTransformHelper:
	'''所有数据转换类的静态辅助方法'''
	@staticmethod
	def GetBoolResultFromBytes( result, byteTransform ):
		'''将指定的OperateResult类型转化'''
		try:
			if result.IsSuccess:
				return OperateResult.CreateSuccessResult(byteTransform.TransBool(result.Content , 0 ))
			else:
				return OperateResult.CreateFromFailedResult(result)
		except Exception as ex:
			return OperateResult.CreateFailedResult("数据转化失败，源数据：" + SoftBasic.ByteToHexString( result.Content ) + " 消息：" + str(ex))
	@staticmethod
	def GetByteResultFromBytes( result, byteTransform ):
		'''将指定的OperateResult类型转化'''
		try:
			if result.IsSuccess:
				return OperateResult.CreateSuccessResult(byteTransform.TransByte(result.Content , 0 ))
			else:
				return OperateResult.CreateFromFailedResult(result)
		except Exception as ex:
			return OperateResult.CreateFailedResult("数据转化失败，源数据：" + SoftBasic.ByteToHexString( result.Content ) + " 消息：" + str(ex))
	@staticmethod
	def GetInt16ResultFromBytes( result, byteTransform ):
		'''将指定的OperateResult类型转化'''
		try:
			if result.IsSuccess:
				return OperateResult.CreateSuccessResult(byteTransform.TransInt16(result.Content , 0 ))
			else:
				return OperateResult.CreateFromFailedResult(result)
		except Exception as ex:
			return OperateResult.CreateFailedResult("数据转化失败，源数据：" + SoftBasic.ByteToHexString( result.Content ) + " 消息：" + str(ex))
	@staticmethod
	def GetUInt16ResultFromBytes( result, byteTransform ):
		'''将指定的OperateResult类型转化'''
		try:
			if result.IsSuccess:
				return OperateResult.CreateSuccessResult(byteTransform.TransUInt16(result.Content , 0 ))
			else:
				return OperateResult.CreateFromFailedResult(result)
		except Exception as ex:
			return OperateResult.CreateFailedResult("数据转化失败，源数据：" + SoftBasic.ByteToHexString( result.Content ) + " 消息：" + str(ex))
	@staticmethod
	def GetInt32ResultFromBytes( result, byteTransform ):
		'''将指定的OperateResult类型转化'''
		try:
			if result.IsSuccess:
				return OperateResult.CreateSuccessResult(byteTransform.TransInt32(result.Content , 0 ))
			else:
				return OperateResult.CreateFromFailedResult(result)
		except Exception as ex:
			return OperateResult.CreateFailedResult("数据转化失败，源数据：" + SoftBasic.ByteToHexString( result.Content ) + " 消息：" + str(ex))
	@staticmethod
	def GetUInt32ResultFromBytes( result, byteTransform ):
		'''将指定的OperateResult类型转化'''
		try:
			if result.IsSuccess:
				return OperateResult.CreateSuccessResult(byteTransform.TransUInt32(result.Content , 0 ))
			else:
				return OperateResult.CreateFromFailedResult(result)
		except Exception as ex:
			return OperateResult.CreateFailedResult("数据转化失败，源数据：" + SoftBasic.ByteToHexString( result.Content ) + " 消息：" + str(ex))
	@staticmethod
	def GetInt64ResultFromBytes( result, byteTransform ):
		'''将指定的OperateResult类型转化'''
		try:
			if result.IsSuccess:
				return OperateResult.CreateSuccessResult(byteTransform.TransInt64(result.Content , 0 ))
			else:
				return OperateResult.CreateFromFailedResult(result)
		except Exception as ex:
			return OperateResult.CreateFailedResult("数据转化失败，源数据：" + SoftBasic.ByteToHexString( result.Content ) + " 消息：" + str(ex))
	@staticmethod
	def GetUInt64ResultFromBytes( result, byteTransform ):
		'''将指定的OperateResult类型转化'''
		try:
			if result.IsSuccess:
				return OperateResult.CreateSuccessResult(byteTransform.TransUInt64(result.Content , 0 ))
			else:
				return OperateResult.CreateFromFailedResult(result)
		except Exception as ex:
			return OperateResult.CreateFailedResult("数据转化失败，源数据：" + SoftBasic.ByteToHexString( result.Content ) + " 消息：" + str(ex))
	@staticmethod
	def GetSingleResultFromBytes( result, byteTransform ):
		'''将指定的OperateResult类型转化'''
		try:
			if result.IsSuccess:
				return OperateResult.CreateSuccessResult(byteTransform.TransSingle(result.Content , 0 ))
			else:
				return OperateResult.CreateFromFailedResult(result)
		except Exception as ex:
			return OperateResult.CreateFailedResult("数据转化失败，源数据：" + SoftBasic.ByteToHexString( result.Content ) + " 消息：" + str(ex))
	@staticmethod
	def GetDoubleResultFromBytes( result, byteTransform ):
		'''将指定的OperateResult类型转化'''
		try:
			if result.IsSuccess:
				return OperateResult.CreateSuccessResult(byteTransform.TransDouble(result.Content , 0 ))
			else:
				return OperateResult.CreateFromFailedResult(result)
		except Exception as ex:
			return OperateResult.CreateFailedResult("数据转化失败，源数据：" + SoftBasic.ByteToHexString( result.Content ) + " 消息：" + str(ex))
	@staticmethod
	def GetStringResultFromBytes( result, byteTransform ):
		'''将指定的OperateResult类型转化'''
		try:
			if result.IsSuccess:
				return OperateResult.CreateSuccessResult(byteTransform.TransString(result.Content , 0, len(result.Content), 'ascii' ))
			else:
				return OperateResult.CreateFromFailedResult(result)
		except Exception as ex:
			return OperateResult.CreateFailedResult("数据转化失败，源数据：" + SoftBasic.ByteToHexString( result.Content ) + " 消息：" + str(ex))


class SoftBasic:
	'''系统运行的基础方法，提供了一些基本的辅助方法'''
	@staticmethod
	def GetSizeDescription(size):
		'''获取指定数据大小的文本描述字符串'''
		if size < 1000:
			return str(size) + " B"
		elif size < (1000 * 1000):
			data = float(size) / 1024
			return '{:.2f}'.format(data) + " Kb"
		elif size < (1000 * 1000 * 1000):
			data = float(size) / 1024 / 1024
			return '{:.2f}'.format(data) + " Mb"
		else:
			data = float(size) / 1024 / 1024 / 1024
			return '{:.2f}'.format(data) + " Gb"
	@staticmethod
	def ByteToHexString(inBytes,segment=' '):
		'''将字节数组转换成十六进制的表示形式，需要传入2个参数，数据和分隔符，该方法还存在一点问题'''
		str_list = []
		for byte in inBytes:
			str_list.append('{:02X}'.format(byte))
		return segment.join(str_list)
	@staticmethod
	def ByteToBoolArray( InBytes, length ):
		'''从字节数组中提取bool数组变量信息'''
		if InBytes == None:
			return None
		if length > len(InBytes) * 8:
			length = len(InBytes) * 8
		buffer = []
		for  i in range(length):
			index = i // 8
			offect = i % 8

			temp = 0
			if offect == 0 : temp = 0x01
			elif offect == 1 : temp = 0x02
			elif offect == 2 : temp = 0x04
			elif offect == 3 : temp = 0x08
			elif offect == 4 : temp = 0x10
			elif offect == 5 : temp = 0x20
			elif offect == 6 : temp = 0x40
			elif offect == 7 : temp = 0x80

			if (InBytes[index] & temp) == temp:
				buffer.append(True)
			else:
				buffer.append(False)
		return buffer
	@staticmethod
	def BoolArrayToByte( array ):
		if (array == None) : return None

		length = 0
		if len(array) % 8 == 0:
			length = int(len(array) / 8)
		else:
			length = int(len(array) / 8) + 1
		buffer = bytearray(length)

		for i in range(len(array)):
			index = i // 8
			offect = i % 8

			temp = 0
			if offect == 0 : temp = 0x01
			elif offect == 1 : temp = 0x02
			elif offect == 2 : temp = 0x04
			elif offect == 3 : temp = 0x08
			elif offect == 4 : temp = 0x10
			elif offect == 5 : temp = 0x20
			elif offect == 6 : temp = 0x40
			elif offect == 7 : temp = 0x80

			if array[i] : buffer[index] += temp
		return buffer
	@staticmethod
	def HexStringToBytes( hex ):
		'''将hex字符串转化为byte数组'''
		return bytes.fromhex(hex)
	@staticmethod
	def BytesArrayExpandToLengthEven(array):
		'''扩充一个整型的数据长度为偶数个'''
		if len(array) % 2 == 1:
			array.append(0)
		return array

class NetworkBase:
	'''网络基础类的核心'''
	Token = uuid.UUID('{00000000-0000-0000-0000-000000000000}')
	CoreSocket = socket.socket()
	def Receive(self,socket,length):
		'''接收固定长度的字节数组'''
		totle = 0
		data = bytearray()
		try:
			while totle < length:
				data.extend(socket.Receive(length-totle))
				totle += len(data)
			return OperateResult.CreateSuccessResult(data)
		except Exception as e:
			result = OperateResult()
			result.Message = str(e)
			return result
	def Send(self,socket,data):
		'''发送消息给套接字，直到完成的时候返回'''
		try:
			socket.send(data)
			return OperateResult.CreateSuccessResult()
		except Exception as e:
			return OperateResult.CreateFailedResult(str(e))

	def CreateSocketAndConnect(self,ipAddress,port,timeout = 10000):
		'''创建一个新的socket对象并连接到远程的地址，默认超时时间为10秒钟'''
		try:
			socketTmp = socket.socket()
			socketTmp.connect((ipAddress,port))
			return OperateResult.CreateSuccessResult(socketTmp)
		except Exception as e:
			return OperateResult.CreateFailedResult(str(e))
	def ReceiveMessage( self, socket, timeOut, netMsg ):
		'''接收一条完整的数据，使用异步接收完成，包含了指令头信息'''
		result = OperateResult()
		headResult = self.Receive( socket, netMsg.ProtocolHeadBytesLength() )
		if headResult.IsSuccess == False:
			result.CopyErrorFromOther(headResult)
			return result
		netMsg.HeadBytes = headResult.Content
		if netMsg.CheckHeadBytesLegal( self.Token.bytes ) == False:
			# 令牌校验失败
			if socket != None: socket.close()
			result.Message = StringResources.TokenCheckFailed()
			return result

		contentLength = netMsg.GetContentLengthByHeadBytes( )
		if contentLength == 0:
			netMsg.ContentBytes = bytearray(0)
		else:
			contentResult = self.Receive( socket, contentLength )
			if contentResult.IsSuccess == False:
				result.CopyErrorFromOther( contentResult )
				return result
			netMsg.ContentBytes = contentResult.Content
		
		if netMsg.ContentBytes == None: netMsg.ContentBytes = bytearray(0)
		result.Content = netMsg
		result.IsSuccess = True
		return result

class NetworkDoubleBase(NetworkBase):
	'''支持长连接，短连接两个模式的通用客户端基类'''
	byteTransform = ByteTransform()
	ipAddress = "127.0.0.1"
	port = 10000
	isPersistentConn = False
	isSocketError = False
	receiveTimeOut = 10000
	isUseSpecifiedSocket = False
	interactiveLock = threading.Lock()
	iNetMessage = INetMessage()
	
	def SetPersistentConnection( self ):
		'''在读取数据之前可以调用本方法将客户端设置为长连接模式，相当于跳过了ConnectServer的结果验证，对异形客户端无效'''
		self.isPersistentConn = True
	def ConnectServer( self ):
		'''切换短连接模式到长连接模式，后面的每次请求都共享一个通道'''
		self.isPersistentConn = True
		result = OperateResult( )
		# 重新连接之前，先将旧的数据进行清空
		if super().CoreSocket != None: 
			super().CoreSocket.close()

		rSocket = self.CreateSocketAndInitialication( )
		if rSocket.IsSuccess == False:
			self.isSocketError = True
			rSocket.Content = None
			result.Message = rSocket.Message
		else:
			super().CoreSocket = rSocket.Content
			result.IsSuccess = True
		return result
	def ConnectClose( self ):
		'''在长连接模式下，断开服务器的连接，并切换到短连接模式'''
		result = OperateResult( )
		self.isPersistentConn = False

		self.interactiveLock.acquire()
		# 额外操作
		result = self.ExtraOnDisconnect( super().CoreSocket )
		# 关闭信息
		if super().CoreSocket != None : super().CoreSocket.close()
		super().CoreSocket = None
		self.interactiveLock.release( )
		return result
	

	# 初始化的信息方法和连接结束的信息方法，需要在继承类里面进行重新实现
	def InitializationOnConnect( self, socket ):
		'''连接上服务器后需要进行的初始化操作'''
		return OperateResult.CreateSuccessResult()
	def ExtraOnDisconnect( self, socket ):
		'''在将要和服务器进行断开的情况下额外的操作，需要根据对应协议进行重写'''
		return OperateResult.CreateSuccessResult()
	
	def GetAvailableSocket( self ):
		'''获取本次操作的可用的网络套接字'''
		if self.isPersistentConn :
			# 如果是异形模式
			if self.isUseSpecifiedSocket :
				if self.isSocketError:
					return OperateResult.CreateFailedResult( '连接不可用' )
				else:
					return OperateResult.CreateSuccessResult( self.CoreSocket )
			else:
				# 长连接模式
				if self.isSocketError or self.CoreSocket == None :
					connect = self.ConnectServer( )
					if connect.IsSuccess == False:
						self.isSocketError = True
						return OperateResult.CreateFailedResult( connect.Message )
					else:
						self.isSocketError = False
						return OperateResult.CreateSuccessResult( self.CoreSocket )
				else:
					return OperateResult.CreateSuccessResult( self.CoreSocket )
		else:
			# 短连接模式
			return self.CreateSocketAndInitialication( )

	def CreateSocketAndInitialication( self ):
		'''连接并初始化网络套接字'''
		result = super().CreateSocketAndConnect( self.ipAddress, self.port, 10000 )
		if result.IsSuccess:
			# 初始化
			initi = self.InitializationOnConnect( result.Content )
			if initi.IsSuccess == False:
				if result.Content !=None : result.Content.Close( )
				result.IsSuccess = initi.IsSuccess
				result.CopyErrorFromOther( initi )
		return result

	def ReadFromCoreSocketServer( self, socket, send ):
		'''在其他指定的套接字上，使用报文来通讯，传入需要发送的消息，返回一条完整的数据指令'''
		read = self.ReadFromCoreServerBase( socket, send )
		if read.IsSuccess == False: return OperateResult.CreateFromFailedResult( read )

		# 拼接结果数据
		Content = bytearray(len(read.Content1) + len(read.Content2))
		if len(read.Content1) > 0 : 
			Content[0:len(read.Content1)] = read.Content1
		if len(read.Content2) > 0 : 
			Content[len(read.Content1):len(Content)] = read.Content2
		return OperateResult.CreateSuccessResult( Content )

	def ReadFromCoreServer( self, send ):
		'''使用底层的数据报文来通讯，传入需要发送的消息，返回一条完整的数据指令'''
		result = OperateResult( )
		self.interactiveLock.acquire()
		# 获取有用的网络通道，如果没有，就建立新的连接
		resultSocket = self.GetAvailableSocket( )
		if resultSocket.IsSuccess == False:
			self.isSocketError = True
			self.interactiveLock.release()
			result.CopyErrorFromOther( resultSocket )
			return result

		read = self.ReadFromCoreSocketServer( resultSocket.Content, send )
		if read.IsSuccess :
			self.isSocketError = False
			result.IsSuccess = read.IsSuccess
			result.Content = read.Content
			result.Message = StringResources.SuccessText
			# string tmp2 = BasicFramework.SoftBasic.ByteToHexString( result.Content, '-' )
		else:
			self.isSocketError = True
			result.CopyErrorFromOther( read )

		self.interactiveLock.release()
		if self.isPersistentConn==False:
			if resultSocket.Content != None:
				resultSocket.Content.close()
		return result
		
	def ReadFromCoreServerBase( self, socket, send ):
		'''使用底层的数据报文来通讯，传入需要发送的消息，返回最终的数据结果，被拆分成了头子节和内容字节信息'''
		self.iNetMessage.SendBytes = send
		sendResult = super().Send( socket, send )
		if sendResult.IsSuccess == False:
			if socket!= None : socket.close( )
			return OperateResult.CreateFromFailedResult( sendResult )

		# 接收超时时间大于0时才允许接收远程的数据
		if (self.receiveTimeOut >= 0):
			# 接收数据信息
			resultReceive = self.ReceiveMessage(socket, 10000, self.iNetMessage)
			if resultReceive.IsSuccess == False:
				socket.Close( )
				return OperateResult.CreateFailedResult( "Receive data timeout: " + self.receiveTimeOut )
			return OperateResult.CreateSuccessResult( resultReceive.Content.HeadBytes, resultReceive.Content.ContentBytes )
		else:
			return OperateResult.CreateSuccessResult( bytearray(0), bytearray(0) )

	def GetBoolResultFromBytes( self, result ):
		'''将指定的OperateResult类型转化'''
		return ByteTransformHelper.GetBoolResultFromBytes( result, self.byteTransform)
	def GetByteResultFromBytes( self, result ):
		'''将指定的OperateResult类型转化'''
		return ByteTransformHelper.GetByteResultFromBytes( result, self.byteTransform)
	def GetInt16ResultFromBytes( self, result ):
		'''将指定的OperateResult类型转化'''
		return ByteTransformHelper.GetInt16ResultFromBytes( result, self.byteTransform)
	def GetUInt16ResultFromBytes( self, result ):
		'''将指定的OperateResult类型转化'''
		return ByteTransformHelper.GetUInt16ResultFromBytes( result, self.byteTransform)
	def GetInt32ResultFromBytes( self, result ):
		'''将指定的OperateResult类型转化'''
		return ByteTransformHelper.GetInt32ResultFromBytes( result, self.byteTransform )
	def GetUInt32ResultFromBytes( self, result ):
		'''将指定的OperateResult类型转化'''
		return ByteTransformHelper.GetUInt32ResultFromBytes( result, self.byteTransform )
	def GetInt64ResultFromBytes( self, result ):
		'''将指定的OperateResult类型转化'''
		return ByteTransformHelper.GetInt64ResultFromBytes( result, self.byteTransform )
	def GetUInt64ResultFromBytes( self, result ):
		'''将指定的OperateResult类型转化'''
		return ByteTransformHelper.GetUInt64ResultFromBytes( result, self.byteTransform )
	def GetSingleResultFromBytes( self, result ):
		'''将指定的OperateResult类型转化'''
		return ByteTransformHelper.GetSingleResultFromBytes( result, self.byteTransform )
	def GetDoubleResultFromBytes( self, result ):
		'''将指定的OperateResult类型转化'''
		return ByteTransformHelper.GetDoubleResultFromBytes( result, self.byteTransform )
	def GetStringResultFromBytes( self, result ):
		'''将指定的OperateResult类型转化'''
		return ByteTransformHelper.GetStringResultFromBytes( result, self.byteTransform )

class NetworkDeviceBase(NetworkDoubleBase):
	'''设备类的基类，提供了基础的字节读写方法'''
	# 单个数据字节的长度，西门子为2，三菱，欧姆龙，modbusTcp就为1
	WordLength = 1
	def Read( self, address, length ):
		'''从设备读取原始数据'''
		return OperateResult( )
	def Write( self, address, value ):
		'''将原始数据写入设备'''
		return OperateResult()
	def ReadInt16( self, address, length = None ):
		'''读取设备的short类型的数据'''
		if(length == None):
			return self.GetInt16ResultFromBytes( self.Read( address, self.WordLength ) )
		else:
			read = self.Read(address,length*self.WordLength)
			if read.IsSuccess == False:
				return OperateResult.CreateFromFailedResult(read)
			return OperateResult.CreateSuccessResult(self.byteTransform.TransInt16Array(read.Content,0,length))
	def ReadUInt16( self, address, length = None ):
		'''读取设备的ushort数据类型的数据'''
		if length == None:
			return self.GetUInt16ResultFromBytes(self.Read(address,self.WordLength))
		else:
			read = self.Read(address,length*self.WordLength)
			if read.IsSuccess == False:
				return OperateResult.CreateFromFailedResult(read)
			return OperateResult.CreateSuccessResult(self.byteTransform.TransUInt16Array(read.Content,0,length))
	def ReadInt32( self, address, length = None ):
		'''读取设备的int类型的数据'''
		if length == None:
			return self.GetInt32ResultFromBytes( self.Read( address, 2 * self.WordLength ) )
		else:
			read = self.Read(address,2*length*self.WordLength)
			if read.IsSuccess == False:
				return OperateResult.CreateFromFailedResult(read)
			return OperateResult.CreateSuccessResult(self.byteTransform.TransInt32Array(read.Content,0,length))
	def ReadUInt32( self, address, length = None ):
		'''读取设备的uint数据类型的数据'''
		if length == None:
			return self.GetUInt32ResultFromBytes(self.Read(address,2 * self.WordLength))
		else:
			read = self.Read(address,2*length*self.WordLength)
			if read.IsSuccess == False:
				return OperateResult.CreateFromFailedResult(read)
			return OperateResult.CreateSuccessResult(self.byteTransform.TransUInt32Array(read.Content,0,length))
	def ReadFloat( self, address, length = None ):
		'''读取设备的float类型的数据'''
		if length == None:
			return self.GetSingleResultFromBytes( self.Read( address, 2 * self.WordLength ) )
		else:
			read = self.Read(address,2*length*self.WordLength)
			if read.IsSuccess == False:
				return OperateResult.CreateFromFailedResult(read)
			return OperateResult.CreateSuccessResult(self.byteTransform.TransSingleArray(read.Content,0,length))
	def ReadInt64( self, address, length = None ):
		'''读取设备的long类型的数组'''
		if length == None:
			return self.GetInt64ResultFromBytes( self.Read( address, 4 * self.WordLength) )
		else:
			read = self.Read(address,4*length*self.WordLength)
			if read.IsSuccess == False:
				return OperateResult.CreateFromFailedResult(read)
			return OperateResult.CreateSuccessResult(self.byteTransform.TransInt64Array(read.Content,0,length))
	def ReadUInt64( self, address, length = None ):
		'''读取设备的long类型的数组'''
		if length == None:
			return self.GetUInt64ResultFromBytes( self.Read( address, 4 * self.WordLength) )
		else:
			read = self.Read(address,4*length*self.WordLength)
			if read.IsSuccess == False:
				return OperateResult.CreateFromFailedResult(read)
			return OperateResult.CreateSuccessResult(self.byteTransform.TransUInt64Array(read.Content,0,length))
	def ReadDouble( self, address, length = None ):
		'''读取设备的long类型的数组'''
		if length == None:
			return self.GetDoubleResultFromBytes( self.Read( address, 4 * self.WordLength) )
		else:
			read = self.Read(address,4*length*self.WordLength)
			if read.IsSuccess == False:
				return OperateResult.CreateFromFailedResult(read)
			return OperateResult.CreateSuccessResult(self.byteTransform.TransDoubleArray(read.Content,0,length))
	def ReadString( self, address, length ):
		return self.GetStringResultFromBytes( self.Read( address, length ) )
	
	def WriteInt16( self, address, value ):
		'''向设备中写入short数据或是数组，返回是否写入成功'''
		if type(value) == list:
			return self.Write( address, self.byteTransform.Int16ArrayTransByte( value ) )
		else:
			return self.WriteInt16( address, [value] )
	def WriteUInt16( self, address, value ):
		'''向设备中写入short数据或是数组，返回是否写入成功'''
		if type(value) == list:
			return self.Write( address, self.byteTransform.UInt16ArrayTransByte( value ) )
		else:
			return self.WriteUInt16( address, [value] )
	def WriteInt32( self, address, value ):
		'''向设备中写入int数据，返回是否写入成功'''
		if type(value) == list:
			return self.Write( address, self.byteTransform.Int32ArrayTransByte(value) )
		else:
			return self.WriteInt32( address, [value])
	def WriteUInt32( self, address, value):
		'''向设备中写入uint数据，返回是否写入成功'''
		if type(value) == list:
			return self.Write( address, self.byteTransform.UInt32ArrayTransByte(value) )
		else:
			return self.WriteUInt32( address, [value] )
	def WriteFloat( self, address, value ):
		'''向设备中写入float数据，返回是否写入成功'''
		if type(value) == list:
			return self.Write( address, self.byteTransform.FloatArrayTransByte(value) )
		else:
			return self.WriteFloat(address, [value])
	def WriteInt64( self, address, value ):
		'''向设备中写入long数据，返回是否写入成功'''
		if type(value) == list:
			return self.Write( address,  self.byteTransform.Int64ArrayTransByte(value))
		else:
			return self.WriteInt64( address, [value] )
	def WriteUInt64( self, address, value ):
		'''向设备中写入ulong数据，返回是否写入成功'''
		if type(value) == list:
			return self.Write( address,  self.byteTransform.UInt64ArrayTransByte(value))
		else:
			return self.WriteUInt64( address, [value] )
	def WriteDouble( self, address, value ):
		'''向设备中写入double数据，返回是否写入成功'''
		if type(value) == list:
			return self.Write( address, self.byteTransform.DoubleArrayTransByte(value) )
		else:
			return self.WriteDouble( address, [value] )
	def WriteString( self, address, value ):
		'''向设备中写入string数据，编码为ascii，返回是否写入成功'''
		return self.Write( address, self.byteTransform.StringTransByte( value, 'ascii' ) )

class ModbusTcpNet(NetworkDeviceBase):
	'''Modbus-Tcp协议的客户端通讯类，方便的和服务器进行数据交互'''
	station = 1
	softIncrementCount = None
	isAddressStartWithZero = True
	def __init__(self, ipAddress = '127.0.0.1', port = 502, station = 1):
		self.WordLength = 1
		self.softIncrementCount = SoftIncrementCount( 65536, 0 )
		self.station = station
		self.ipAddress = ipAddress
		self.port = port
		self.byteTransform = ReverseWordTransform()
	def SetIsMultiWordReverse( self, value ):
		self.byteTransform.IsMultiWordReverse = value
	def GetIsMultiWordReverse( self ):
		return self.byteTransform.IsMultiWordReverse
	


# modbus = socket.socket()
# ip_port = ('127.0.0.1',502)
# modbus.connect(ip_port)

# send = b'\x00\x00\x00\x00\x00\x06\x01\x03\x00\x00\x00\x01'
# modbus.send(send)
# recive = modbus.recv(1024)
# aaa = bytearray()
# aaa.extend(recive)
# print(aaa)

# modbus.close()

data = b'\xA2'
print(SoftBasic.ByteToBoolArray(data,8))

ii = 100
data = b'\x64\x00'
# print(SoftBasic.ByteToHexString(struct.pack('<h',ii)))
print(struct.unpack('<h',data)[0])
print(SoftBasic.ByteToHexString(SoftBasic.BoolArrayToByte([True,False,False,True,False,False,False,False,True])))

bytesMy = bytearray(4)
bytesMy[0] = 0x31
bytesMy[1] = 0x32
bytesMy[2] = 0x33
bytesMy[3] = 0x34
print(bytesMy.decode('ascii'))
byteTransform = ByteTransform()
print(byteTransform.TransInt16(data,0))
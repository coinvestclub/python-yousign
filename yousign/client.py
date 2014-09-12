# -*- coding: utf-8 -*-

import hashlib
import logging
import os
import pytz
from utils import pythonize, pretty_xml
from suds.client import Client
from lxml import objectify

#from exceptions import YousignError
class YousignError(Exception):
    def __init__(self, message=None, code=None, short_message=None,
                 *args, **kwargs):
        super(YousignError, self).__init__(message, *args, **kwargs)
        self.message = message
        self.code = code
        self.short_message = short_message

logger = logging.getLogger('yousign')

# class YousignFile():
# 	pass

# class YousignSigner():
# 	pass

class YousignClient():

	test_domain = "apidemo.yousign.fr"
	prod_domain = "api.yousign.fr:8181"

	@property
	def WSDL_SIGN_URL(self):
		return "https://%s/CosignWS/CosignWS?wsdl" % self.domain

	@property
	def WSDL_AUTH_URL(self):
		return "https://%s/AuthenticationWS/AuthenticationWS?wsdl" % self.domain

	@property
	def WSDL_ARCH_URL(self):
		return "https://%s/ArchiveWS/ArchiveWS?wsdl" % self.domain

	"""
	urlsuccess : URL called by Yousign if the signature success
	urlcancel : URL called by Yousign if the signature is cancelled by the signer
	urlerror : URL called by Yousign if an error has been detected during the signature
	urlcallback : URL called by Yousign to follow the process of each signature. We will send in GET these parameters :
		status : status of the signature : 'init' when the IFRAME is opened, 'waiting' when the signer need to enter the code to validate the signature, 'signed' when the signer has signed the document(s), 'signed_complete' when all signers have signed the document(s) (after getting this status, you could call the WS getCosignedFilesFromDemand to get the files signed), 'error' if an error has been detected during the signature.
		token : token used in the IFRAME
	tpl : id of template created into your account parameters. This is used to personnalize the GUI (bouton's color, text, background...). If you do not have access to this functionnality, please contact your sales representative. 
	"""
	config = {
		'xmlns_soapenv' : "http://schemas.xmlsoap.org/soap/envelope/",
		'xmlns_yous'	: "http://www.yousign.com",
		'xmlns_aut'	    : "http://authenticationejb.yousign.com/",
		'urlsuccess'	: "",
		'urlcancel' 	: "",
		'urlerror' 		: "",
		'urlcallback' 	: "",
		'status' 		: "",
		'token' 		: "",
		'tpl' 			: ""
	}

	def __init__(self, username, password, api_key, config={}, debug=False):
		"""
		Here is the hash calculation : sha1(sha1(clearPassword)+sha1(clearPassword))
		"""

		if debug:
			self.domain = self.test_domain
		else:
			self.domain = self.prod_domain

		self.username = username
		self.hash_password = hashlib.sha1(
								hashlib.sha1(password).hexdigest()
								+ hashlib.sha1(password).hexdigest()).hexdigest()
		self.api_key = api_key

		print self.WSDL_AUTH_URL

		self._authClient = Client(self.WSDL_AUTH_URL, username=self.username, password=self.hash_password)
		self._signClient = Client(self.WSDL_SIGN_URL, username=self.username, password=self.hash_password)
		self._archClient = Client(self.WSDL_ARCH_URL, username=self.username, password=self.hash_password)

 		for key in ['xmlns_soapenv', 'xmlns_yous', 'xmlns_aut', 'urlsuccess', 'urlcancel', 'urlerror', 'urlcallback', 'tpl']:
 			if config.has_key(key):
 				self.config[key] = config[key]

	def _ws_request(self, client_type, method, **params):
		if client_type == "auth":
			client = self._authClient
		elif client_type == "arch":
			client = self._archClient
		elif client_type == "sign":
			client = self._signClient

		log_params = params.copy()
		info_msg = 'Calling %s method with params: %s' % (method, log_params)
		logger.info(info_msg)
		try:
			xml = getattr(client.service, method)(**params)
			answer = objectify.fromstring(xml)
			answer = pythonize(answer)
			answer.xml = pretty_xml(unicode(xml))
			logger.debug(xml)
		except Exception as e:
			msg = '%s %s - %s' % (e, e.message, info_msg)
			logger.error(msg)
			raise YousignError(msg)
		# Detect errors and raise exception
		if 'error' in answer.__dict__:
			msg = '%s (code: %s) - %s' % (answer.msg, answer.code, info_msg)
			logger.error(msg)
			raise YousignError(msg, answer.code, answer.msg)
		return answer


	def test_connect(self):
		"""
		return True if connection passed, else False
		"""
		return self._ws_request('auth', 'connect')

	def forge_url_signature(self):
		pass

	def signature_init(self,
				  files,
				  signers,
				  title='',
				  message='',
				  initMailSubject=False,
				  initMail=False,
				  endMailSubject=False,
				  endMail=False,
				  language='FR',
				  mode='IFRAME',
				  archive=False):
		"""
		"""
		if mode != 'IFRAME':
			raise YousignError('Other mode than Iframe not implemented')

		return self._ws_request('sign', 'yous:initCosign',   lstCosignedFile=files,
													lstCosignerInfos=signers,
													title=title,
													message=message,
													initMailSubject=initMailSubject,
													initMail=initMail,
													endMailSubject=endMailSubject,
													endMail=endMail,
													language=language,
													mode=mode,
													archive=archive)

	def get_signed_file(self, signature_id, token='', file_id=''):
		"""
		"""
		return self._ws_request('sign', 'yous:getCosignedFilesFromDemand',
													idDemand=signature_id,
													token=token,
													idFile=file_id)

	def get_signature_infos(self, signature_id, token=''):
		"""
		"""
		return self._ws_request('sign', 'yous:getInfosFromCosignatureDemand',
													idDemand=signature_id,
													token=token)

	def get_signature_list(self, search='', first_result='', count='', status='', date_begin=False, date_end=False):
		"""
		return max 1000 results
		status : COSIGNATURE_EVENT_REQUEST_PENDING, COSIGNATURE_EVENT_OK, COSIGNATURE_EVENT_PROCESSING and COSIGNATURE_EVENT_CANCELLED
		"""
		if date_begin:
			date_begin = str(date_begin.replace(tzinfo=pytz.utc)),
		if date_end:
			date_end = str(date_end.replace(tzinfo=pytz.utc)),
		return self._ws_request('sign', 'yous:getListCosign',
													search=search,
													firstResult=str(first_result),
													count=str(count),
													status=status,
													dateBegin=date_begin,
													dateEnd=date_end
													)

	def cancel_signature(self, signature_id):
		"""
		"""
		return self._ws_request('sign', 'yous:cancelCosignatureDemand',
													idDemand=signature_id)

	def alert_signers(self, signature_id, mail_subject='', mail='', language='FR'):
		"""
		Alert signers if they have no-signed file pending.
		return True if alerts have been sent, false otherwise
		"""
		return self._ws_request('sign', 'yous:cancelCosignatureDemand',
													idDemand=signature_id,
													mailSubject=mail_subject,
													mail=mail,
													language=language
													)

	def archive_create(self, content,
							fileName='',
							subject='',
							date1='',
							date2='',
							type='',
							author='',
							comment='',
							ref='',
							amount='',
							tag='',
							generic1='',
							generic2=''):
		"""
		return uia: unique identifier archive, and file_name

		content : content in base 64 format of the file
		fileName : name of file
		subject : subject of archive
		date1 : specify one date (creation of the document, invoice date, etc.)
		date2 : specify another date
		type : type of file. For example : contrat, invoice, note.
		author : author
		comment : any comment
		ref : reference associated
		amount : amount of contract, invoice for example
		tag : list of tag to add more informations
		generic1 : free list of fields
		generic2 : free list of fields
		"""
		return self._ws_request('arch', 'yous:archive',
							content=content,
							fileName=fileName,
							subject=subject,
							date1=date1,
							date2=date2,
							type=type,
							author=author,
							comment=comment,
							ref=ref,
							amount=amount,
							tag=tag,
							generic1=generic1,
							generic2=generic2)

	def get_archive(self, uia):
		"""
		return file and file_name
		"""
		return self._ws_request('arch', 'yous:getArchiveResponse',
													uia=uia)

	def get_complete_archive(self, uia):
		"""
		return file and file_name + metadatas
		"""
		return self._ws_request('arch', 'yous:getCompleteArchive',
													uia=uia)

if __name__ == "__main__":
	print "test"
	c = YousignClient(username="nico", password="test", api_key="keeyyyy", debug=True)

	print c.test_connect()
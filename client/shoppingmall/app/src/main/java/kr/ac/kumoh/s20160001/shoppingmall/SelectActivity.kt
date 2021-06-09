package kr.ac.kumoh.s20160001.shoppingmall

import android.Manifest
import android.graphics.Bitmap
import android.graphics.BitmapFactory
import android.net.Uri
import androidx.appcompat.app.AppCompatActivity
import android.os.Bundle
import android.provider.MediaStore
import android.util.Log
import android.view.LayoutInflater
import android.view.View
import android.view.animation.AnimationUtils
import android.widget.ImageView
import android.widget.TextView
import android.widget.Toast
import com.google.gson.Gson
import com.google.gson.GsonBuilder
import kr.ac.kumoh.s20160001.shoppingmall.databinding.ActivitySelectBinding
import kr.ac.kumoh.s20160001.shoppingmall.fragment.ResultFragment
import kr.ac.kumoh.s20160001.shoppingmall.fragment.sendFragment
import okhttp3.MediaType
import okhttp3.MultipartBody
import okhttp3.RequestBody
import okhttp3.ResponseBody
import retrofit2.Call
import retrofit2.Callback
import retrofit2.Response
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import java.io.ByteArrayOutputStream
import java.io.File
import java.io.IOException
import java.net.URLEncoder


class SelectActivity : AppCompatActivity() {
    private  val BASE_URL = "http://202.31.200.237:2010"
    //private val BASE_URL = "http://172.16.101.61:8082"
    lateinit var binding: ActivitySelectBinding


    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivitySelectBinding.inflate(layoutInflater)
        val sendfragment = sendFragment()
        val resultfragment = ResultFragment()
        val view = binding.root
        val Uri_S = intent.getStringExtra("Uri")
        val id = intent.getStringExtra("id")
        val Uri = Uri.parse(Uri_S)
        val bundle = Bundle()
        val bundle2 = Bundle()
        val id_int = id!!.toInt()

        bundle.putString("Uri",Uri_S)
        sendfragment.arguments = bundle
        resultfragment.arguments=bundle2

        val transaction = supportFragmentManager.beginTransaction().add(R.id.frameLayout,sendfragment)
        setContentView(view)
        transaction.commit()
        binding.button3.setOnClickListener {
            binding.button3.isClickable = false
            val mDial = LayoutInflater.from(this).inflate(R.layout.dialog_loading,null)
            var builder = LoadingDialog(this)
            builder.setContentView(mDial)
            builder.show()
            val animation = AnimationUtils.loadAnimation(this,R.anim.rotate)
            val loading = mDial.findViewById<ImageView>(R.id.progressBar2)
            val text = mDial.findViewById<TextView>(R.id.test)
            loading.startAnimation(animation)

            var column_idx = 0
            var proj = arrayOf(MediaStore.Images.Media.DATA)
            var cursor = contentResolver.query(Uri,proj,null,null,null)
            if (cursor!!.moveToFirst()){
                column_idx = cursor.getColumnIndexOrThrow(MediaStore.Images.Media.DATA)

            }
            var RealUri = cursor.getString(column_idx)


            //png파일 생성
            val file = File(RealUri)

            var requestBody : RequestBody = RequestBody.create(MediaType.parse("image/*"),file)
            Log.d("반환성공",requestBody.toString())


            var body : MultipartBody.Part = MultipartBody.Part.createFormData("img_file",file.name,requestBody)
            //The gson builder
            var gson : Gson =  GsonBuilder()
                .setLenient()
                .create()
            var retrofit =
                Retrofit.Builder()
                    .baseUrl(BASE_URL)
                    .addConverterFactory(GsonConverterFactory.create(gson))
                    .build()
            var server = retrofit.create(RetrofitService::class.java)
            Log.d("레트로핏 결과 전송", id.toString())
            server.request(id_int,body).enqueue(object: Callback<ResponseBody> {
                override fun onFailure(call: Call<ResponseBody>, t: Throwable) {
                    Log.d("레트로핏 결과 전송", t.message.toString())
                    Toast.makeText(getApplicationContext(), "서버 연결에 실패했습니다.2", Toast.LENGTH_LONG).show();

                }

                override fun onResponse(
                    call: Call<ResponseBody>,
                    response: Response<ResponseBody>
                ) {
                    Log.d("레트로핏 결과 전송", response.code().toString())
                    if (response?.isSuccessful) {

                        val file = response.body()?.byteStream()
                        val bitmap = BitmapFactory.decodeStream(file)
                        val stream = ByteArrayOutputStream()
                        bitmap.compress(Bitmap.CompressFormat.PNG, 100 , stream)
                        val byte = stream.toByteArray()
                        bundle2.putByteArray("img",byte)
                        builder.hide()
                        val transaction2 = supportFragmentManager.beginTransaction().replace(R.id.frameLayout,resultfragment)
                        transaction2.commit()
                        binding.button3.visibility=View.INVISIBLE
                    }
                    else {
                        Log.d("UploadImage", "Response failure = "+response.message());
                        try {
                            Log.d("UploadImage", "Response failure = "+response.errorBody().toString());
                        } catch (e : IOException) {
                            Log.d("UploadImage", "IOException = "+e.message);
                        }

                    }
                }
            })


        }
    }

}
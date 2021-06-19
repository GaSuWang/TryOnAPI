package kr.ac.kumoh.s20160001.shoppingmall

import android.app.Application
import android.content.Context
import android.graphics.Bitmap
import android.graphics.BitmapFactory
import android.net.Uri
import android.provider.MediaStore
import android.util.Log
import android.widget.ImageView
import android.widget.Toast
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.MutableLiveData
import com.google.gson.Gson
import com.google.gson.GsonBuilder
import okhttp3.ResponseBody
import retrofit2.Call
import retrofit2.Callback
import retrofit2.Response
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import java.io.ByteArrayOutputStream

class ViewModel(application: Application) : AndroidViewModel(application) {
    data class Product (var id: String, var name: String, var price: String)
    data class reco_Product (var id: String, var name: String, var price: String)

    val list = MutableLiveData<ArrayList<Product>>()
    val reco_list = MutableLiveData<ArrayList<reco_Product>>()
    private val product = ArrayList<Product>()
    private val reco_product = ArrayList<reco_Product>()
    private  val BASE_URL = "http://202.31.200.237:2010"

    fun getProduct(i: Int) = product[i]
    fun getSize() = product.size

    fun getRecoProduct(i:Int) = reco_product[i]
    fun getRecoSize() = reco_product.size


    fun setImg(id: String?, productImg:ImageView){
        var gson : Gson =  GsonBuilder()
                .setLenient()
                .create()
        var retrofit =
                Retrofit.Builder()
                        .baseUrl(BASE_URL)
                        .addConverterFactory(GsonConverterFactory.create(gson))
                        .build()

        var server = retrofit.create(RetrofitService::class.java)
        server.getimage(id).enqueue(object: Callback<ResponseBody> {
            override fun onFailure(call: Call<ResponseBody>, t: Throwable) {
                Log.d("레트로핏 결과", t.message.toString())
            }
            override fun onResponse(
                    call: Call<ResponseBody>,
                    response: Response<ResponseBody>
            ) {
                val file = response.body()?.byteStream()
                val bitmap = BitmapFactory.decodeStream(file)
                productImg.setImageBitmap(bitmap)
            }
        })
    }

    fun getInfo(){
        for (i in 0 until 50) {
            val id = ""+i
            val name = "테스트이미지"
            val price = "10000원"
            product.add(Product(id, name, price))
        }
    }

    fun getReco(){
        for (i in 0 until 8) {
            val id = ""+i+3
            val name = "테스트이미지"
            val price = "10000원"
            reco_product.add(reco_Product(id, name, price))
        }
    }
}
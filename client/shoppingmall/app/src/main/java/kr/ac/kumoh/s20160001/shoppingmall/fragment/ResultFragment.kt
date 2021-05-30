package kr.ac.kumoh.s20160001.shoppingmall.fragment

import android.content.ContentValues
import android.content.Intent
import android.graphics.Bitmap
import android.graphics.BitmapFactory
import android.net.Uri
import android.os.Build
import android.os.Bundle
import android.os.Environment
import android.provider.MediaStore
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.ImageView
import android.widget.Toast
import androidx.fragment.app.Fragment
import com.google.android.material.floatingactionbutton.FloatingActionButton
import kr.ac.kumoh.s20160001.shoppingmall.R
import java.io.File
import java.io.FileOutputStream
import java.io.OutputStream


class ResultFragment : Fragment() {
    var byte: ByteArray? = null
    lateinit var bitmap: Bitmap
    private lateinit var currentPhotoPath: String
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        arguments?.let {
            byte = it.getByteArray("img")
            bitmap = BitmapFactory.decodeByteArray(byte,0,byte!!.size)
        }
    }

    override fun onCreateView(inflater: LayoutInflater, container: ViewGroup?,
                              savedInstanceState: Bundle?): View? {
        val v = inflater.inflate(R.layout.fragment_result, container, false)
        val btn_save = v.findViewById<FloatingActionButton>(R.id.saveBtn)
        val btn_share = v.findViewById<FloatingActionButton>(R.id.shareBtn)
        val result = v.findViewById<ImageView>(R.id.resultImg)
        result.setImageBitmap(bitmap)

        btn_save.setOnClickListener {

            val filename = "${System.currentTimeMillis()}.png"
            var fos:OutputStream? = null
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
                //getting the contentResolver
                context?.contentResolver?.also { resolver ->
                    val contentValues = ContentValues().apply {
                        put(MediaStore.MediaColumns.DISPLAY_NAME, filename)
                        put(MediaStore.MediaColumns.MIME_TYPE, "image/png")
                        put(MediaStore.MediaColumns.RELATIVE_PATH, Environment.DIRECTORY_PICTURES)
                    }
                    val imageUri: Uri? =
                            resolver.insert(MediaStore.Images.Media.EXTERNAL_CONTENT_URI, contentValues)
                    fos = imageUri?.let { resolver.openOutputStream(it) }
                }
            } else {
                val imagesDir = Environment.getExternalStoragePublicDirectory(Environment.DIRECTORY_PICTURES)
                val image = File(imagesDir, filename)
                fos = FileOutputStream(image)
            }

            fos?.use {
                //Finally writing the bitmap to the output stream that we opened
                bitmap.compress(Bitmap.CompressFormat.PNG, 100, it)
               Toast.makeText(activity,"Saved to Photos",Toast.LENGTH_SHORT).show()
            }

        }
        btn_share.setOnClickListener {
            val intent = Intent(android.content.Intent.ACTION_SEND)
            intent.setType("image/*")
            //intent.putExtra(Intent.EXTRA_STREAM,resultUri)
            val choose = Intent.createChooser(intent,"공유하기")
            startActivity(choose)
        }
        return v
    }
}